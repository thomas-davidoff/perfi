from werkzeug.datastructures import FileStorage
from app.repositories import (
    TransactionsFileRepository,
    TransactionRepository,
    AccountRepository,
    UserRepository,
)
from app.services import UserService, LocalFileService
from uuid import UUID
import csv
from app.utils import StandardDate
from database import TransactionsFileImportStatus
from app.validators import to_uuid
from app.exceptions import ApiError
from datetime import datetime
import json


class FileImportService:
    def __init__(
        self,
        file_service: LocalFileService,
        file_repo: TransactionsFileRepository,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        user_repo: UserRepository,
    ):
        self.file_service = file_service
        self.file_repo = file_repo
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.user_repo = user_repo
        self.user_service: UserService = UserService(user_repo)

    def save_and_preview(
        self, file: FileStorage, user_id: str | UUID, account_id: str | UUID
    ):
        """
        Save the file and extract a preview for user confirmation.
        """

        user_id, account_id = to_uuid(user_id), to_uuid(account_id)

        # validate the file as an accepted type (csv)
        file_is_valid = self._validate_csv(file)

        if not file_is_valid:
            raise ApiError("Invalid file format. CSV required.")

        user_accounts = self.user_service.get_user_accounts(user_id=user_id)
        if not account_id in [a.id for a in user_accounts]:
            raise ApiError(
                f"Invalid account ID: Account with id {account_id} does not exist, or does not belong to user."
            )

        today = StandardDate(datetime.now()).to_string()
        file_name = (
            f"{today}_" + file.filename.replace(" ", "_").replace("-", "_")
        ).lower()

        # Save the file
        # TODO: Wrap save and repo create blocks in a rollback mechanism so a file is not
        # saved if it cannot also be added to the DB
        file_path = self.file_service.save_file(file, user_id, file_name=file_name)
        try:
            preview_data, headers = self._extract_preview(file_path)
        except ValueError as e:
            raise ValueError(f"File validation error: {e}")

        file_record = self.file_repo.create(
            {
                "filename": file_name,
                "file_path": file_path,
                "user_id": user_id,
                "status": TransactionsFileImportStatus.PENDING.value,
                "preview_data": preview_data,
                "account_id": account_id,
            }
        )
        return file_record, headers

    def _extract_preview(self, file_path: str):
        """
        Extract headers and the first 10 rows of the file for preview.
        """
        try:
            with open(file_path, mode="r") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise ValueError("File has no headers.")
                headers = reader.fieldnames
                preview_data = [
                    row for _, row in zip(range(5), reader)
                ]  # First 10 rows
            return preview_data, headers
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    def map_headers(
        self, file_id: str | UUID, mapped_headers: dict, user_id: str | UUID
    ):
        """
        Map file headers to transaction fields and validate the mapping.
        """
        file_id, user_id = to_uuid(file_id), to_uuid(user_id)
        file_record = self.file_repo.get_by_id(id=file_id, user_id=user_id)
        if not file_record:
            raise ValueError("File record not found.")

        # Validate the mapped headers
        transaction_fields = {"amount", "description", "merchant", "date", "category"}
        if not file_record.account_id:
            transaction_fields.add(
                "account_id"
            )  # Add account_id for multi-account imports

        for header in mapped_headers.keys():
            if (
                header not in file_record.preview_data[0]
            ):  # Assuming preview data exists
                raise ApiError(f"Header '{header}' not found in file.")

        # Ensure required fields are mapped
        mapped_fields = set(mapped_headers.values())
        missing_fields = transaction_fields - mapped_fields
        if missing_fields:
            raise ApiError(f"Missing required fields: {', '.join(missing_fields)}")

        self.file_repo.update(
            file_id,
            {
                "mapped_headers": mapped_headers,
                "status": TransactionsFileImportStatus.VALIDATED.value,
            },
            user_id=user_id,
        )

    def import_transactions(self, file_id: str | UUID, user_id: str | UUID):
        """
        Process the file and create transactions in the database.
        """
        file_id, user_id = to_uuid(file_id), to_uuid(user_id)
        file_record = self.file_repo.get_by_id(file_id, user_id=user_id)
        if not file_record:
            raise ApiError("File record not found.")
        if file_record.mapped_headers is None:
            raise ApiError("File must be validated before importing.")

        error_log = {}
        with open(file_record.file_path, mode="r") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader):
                try:
                    mapped_data = {}
                    for header, field in file_record.mapped_headers.items():
                        value = row.get(header)
                        if field == "amount":
                            mapped_data[field] = float(value)
                        elif field == "date":
                            mapped_data[field] = StandardDate(value).date
                        elif field == "account_id":
                            account = self.account_repo.get_by_id(UUID(value))
                            if not account or account.user_id != file_record.user_id:
                                raise ValueError(f"Invalid account_id in row: {value}")
                            mapped_data[field] = account.id
                        else:
                            mapped_data[field] = value

                    if file_record.account_id:
                        mapped_data["account_id"] = file_record.account_id

                    mapped_data["file_id"] = file_record.id

                    existing_transaction = self.transaction_repo.get_where(
                        dict(
                            file_id=file_record.id,
                            date=mapped_data["date"],
                            amount=mapped_data["amount"],
                        )
                    )
                    if existing_transaction:
                        print(
                            f"skipping transaction from row {row_num} with existing ID {existing_transaction.id}"
                        )
                        continue

                    t = self.transaction_repo.create(mapped_data)
                    print(f"transaction imported with id {t.id}")
                except Exception as e:
                    print(f"appending {str(e)} to errors for row number {row_num}")
                    error_log[row_num] = str(e)

        update_data = {
            "status": (
                TransactionsFileImportStatus.IMPORTED.value
                if len(error_log.keys()) == 0
                else TransactionsFileImportStatus.FAILED.value
            ),
            "error_log": json.loads(json.dumps(error_log)),
        }
        self.file_repo.update(
            file_id,
            data=update_data,
            user_id=user_id,
        )

    def _validate_csv(self, file: FileStorage | None):
        return self.file_service.is_csv(file)

    def list_files_for_user(self, user_id: str | UUID):
        user_id = to_uuid(user_id)
        user = self.user_service.get_by_id(user_id=user_id)
        return [t.compact() for t in user.transactions_files]

    def get_file_metadata(self, user_id: str | UUID, file_id: str | UUID):
        user_id, file_id = to_uuid(user_id), to_uuid(file_id)
        f = self.file_repo.get_by_id(file_id, user_id=user_id)
        return f.to_dict()


def create_file_import_service(
    upload_folder: str | UUID = "uploads",
) -> FileImportService:
    account_repo = AccountRepository()
    file_service = LocalFileService(upload_folder=upload_folder)
    transaction_repo = TransactionRepository()
    transaction_file_repo = TransactionsFileRepository()
    account_repo = AccountRepository()
    user_repo = UserRepository()
    return FileImportService(
        file_service=file_service,
        transaction_repo=transaction_repo,
        file_repo=transaction_file_repo,
        account_repo=account_repo,
        user_repo=user_repo,
    )
