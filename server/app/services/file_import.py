from werkzeug.datastructures import FileStorage
from app.repositories import (
    TransactionsFileRepository,
    TransactionRepository,
    AccountRepository,
    UserRepository,
)
from app.services import UserService
from uuid import UUID
import csv
from app.utils import StandardDate
from database import TransactionsFileImportStatus


class FileImportService:
    def __init__(
        self,
        file_service,
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

    def save_and_preview(self, file: FileStorage, user_id: str, account_id: UUID):
        """
        Save the file and extract a preview for user confirmation.
        """
        # Validate account
        # get user accounts
        # user_accounts = self.user_repo.get_by_id(user_id).accounts
        # account_ids = [a.id for a in user_accounts]

        user_accounts = self.user_service.get_user_accounts(user_id=user_id)
        if not account_id in [a.id for a in user_accounts]:
            raise ValueError(
                f"Invalid account ID: Account with id {account_id} does not belong to user."
            )

        # Save the file
        file_path = self.file_service.save_file(file, user_id)
        try:
            preview_data, headers = self._extract_preview(file_path)
        except ValueError as e:
            raise ValueError(f"File validation error: {e}")

        # Save file metadata with account association
        file_record = self.file_repo.create(
            {
                "filename": file.filename,
                "file_path": file_path,
                "user_id": user_id,
                "status": TransactionsFileImportStatus.PENDING.value,
                "preview_data": preview_data,
                "account_id": account_id,  # Optional for single-account imports
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
                    row for _, row in zip(range(10), reader)
                ]  # First 10 rows
            return preview_data, headers
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    def map_headers(self, file_id: UUID, mapped_headers: dict):
        """
        Map file headers to transaction fields and validate the mapping.
        """
        file_record = self.file_repo.get_by_id(file_id)
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
                raise ValueError(f"Header '{header}' not found in file.")

        # Ensure required fields are mapped
        mapped_fields = set(mapped_headers.values())
        missing_fields = transaction_fields - mapped_fields
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        self.file_repo.update(
            file_id,
            {
                "mapped_headers": mapped_headers,
                "status": TransactionsFileImportStatus.VALIDATED.value,
            },
        )

    def import_transactions(self, file_id: UUID):
        """
        Process the file and create transactions in the database.
        """
        file_record = self.file_repo.get_by_id(file_id)
        if not file_record:
            raise ValueError("File record not found.")
        if file_record.status != TransactionsFileImportStatus.VALIDATED.value:
            raise ValueError("File must be validated before importing.")

        try:
            with open(file_record.file_path, mode="r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Map data to Transaction fields
                    mapped_data = {}
                    for header, field in file_record.mapped_headers.items():
                        value = row.get(header)
                        # Handle type conversions
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

                    # Use file's account_id for single-account imports
                    if file_record.account_id:
                        mapped_data["account_id"] = file_record.account_id

                    self.transaction_repo.create(mapped_data)

            self.file_repo.update(
                file_id, {"status": TransactionsFileImportStatus.IMPORTED.value}
            )
        except Exception as e:
            self.file_repo.update(
                file_id,
                {
                    "status": TransactionsFileImportStatus.FAILED.value,
                    "error_log": str(e),
                },
            )
            raise

    def _validate_csv(self, file: FileStorage | None):
        return self.file_service.is_csv(file)
