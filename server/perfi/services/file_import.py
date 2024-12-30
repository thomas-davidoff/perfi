from typing import List, Dict, Union, Tuple
from uuid import UUID
from fastapi import UploadFile
from datetime import datetime
import csv
import json
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.database import (
    TransactionsFileImportStatus,
    User,
    Account,
    TransactionsFile,
)
from perfi.core.exc import ServiceError, RepositoryError, ResourceNotFound
from perfi.core.utils import StandardDate
from perfi.core.repositories import (
    TransactionsFileRepository,
    TransactionRepository,
    AccountRepository,
    UserRepository,
)
from .local_file import LocalFileService
import logging

from perfi.schemas import (
    UploadTransactionFileInfo,
    TransactionFileCompact,
    TransactionsFile as TransactionsFileSchema,
)

from pydantic import ValidationError as PydanticValidationError

from perfi.schemas.transaction import TransactionRequest


from .resource_service import ResourceService

logger = logging.getLogger(__name__)


class FileImportService(ResourceService[TransactionsFile]):
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

    async def save_and_preview(
        self, file: UploadFile, user: User, account: Account
    ) -> UploadTransactionFileInfo:
        """
        Save the file and extract a preview for user confirmation.
        """
        # Validate CSV file
        if not await self.file_service.is_csv(file):
            raise ServiceError("Invalid file format. CSV required.")

        today = StandardDate(datetime.now()).to_string()
        file_name = f"{today}_{file.filename.replace(' ', '_').lower()}"

        # Save file
        file_path = await self.file_service.save_file(file, str(user.id), file_name)

        # Extract preview
        try:
            preview_data, headers = self._extract_preview(file_path)
        except ValueError as e:
            raise ServiceError(f"File validation error: {e}")

        # Save record in the database
        try:
            file_record = await self.file_repo.create(
                data={
                    "filename": file_name,
                    "file_path": file_path,
                    "user_id": user.id,
                    "status": TransactionsFileImportStatus.PENDING.value,
                    "preview_data": json.dumps(preview_data),
                    "account_id": account.id,
                },
            )
        except RepositoryError as e:
            logger.error(e)
            raise ServiceError(str(e)) from e

        file_data = TransactionFileCompact.model_validate(file_record)
        return UploadTransactionFileInfo(file=file_data, headers=headers)

    def _extract_preview(self, file_path: str) -> Tuple[Dict, List[str]]:
        """
        Extract headers and the first 10 rows of the file for preview.
        """
        try:
            with open(file_path, mode="r") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise ValueError("File has no headers.")
                headers = reader.fieldnames
                preview_data = [row for _, row in zip(range(10), reader)]
            return preview_data, headers
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    async def map_headers(
        self,
        file_record: TransactionsFile,
        mapped_headers: Dict,
    ) -> None:
        """
        Map file headers to transaction fields and validate the mapping.
        """
        if not file_record:
            raise ServiceError("File record not found.")

        for header in mapped_headers.keys():
            if header not in json.loads(file_record.preview_data)[0]:
                raise ServiceError(f"Header '{header}' not found in file.")

        if "account_id" in mapped_headers.keys():
            raise ServiceError("Cannot manually map account ID.")

        required_fields = TransactionRequest.required_fields()

        # Ensure required fields are mapped
        mapped_fields = set(mapped_headers.values())
        missing_fields = required_fields - mapped_fields - {"account_id"}
        if missing_fields:
            raise ServiceError(f"Missing required fields: {', '.join(missing_fields)}")

        return await self.file_repo.update_by_id(
            file_record.id,
            {
                "mapped_headers": json.dumps(mapped_headers),
                "status": TransactionsFileImportStatus.VALIDATED.value,
            },
        )

    async def import_transactions(self, file_record: TransactionsFile) -> Dict:
        """
        Process the file and create transactions in the database.
        """
        if not file_record:
            raise ServiceError("File record not found.")
        if not file_record.mapped_headers:
            raise ServiceError("File must be validated before importing.")

        errs = []
        warns = []
        messages = []

        try:
            with open(file_record.file_path, mode="r") as f:
                mapped_headers = json.loads(file_record.mapped_headers)

                logger.debug(mapped_headers)

                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader):
                    try:
                        mapped = {v: row[k] for k, v in mapped_headers.items()}
                        mapped["account_id"] = str(file_record.account_id)
                        logger.debug(mapped)
                        req = TransactionRequest.model_validate_json(json.dumps(mapped))

                        logger.debug(req.model_dump())

                        # find existing
                        existing_transaction = await self.transaction_repo.get_where(
                            filter_data=req.model_dump(
                                include=["merchant", "date", "amount"]
                            ),
                        )

                        if existing_transaction:
                            msg = f"Duplicate transaction detected while importing row num {row_num}"
                            logger.warning(msg)
                            warns.append(msg)
                            continue

                        await self.transaction_repo.create(req.model_dump())
                        logger.debug(f"Transaction in row {row_num} imported")
                        messages.append(f"row {row_num} successfully imported")

                    except PydanticValidationError as e:
                        logger.error((str(e)))

                        logger.error(e.errors())

                        problems = e.errors()
                        for err in problems:
                            errs.append(
                                {
                                    "error": f"Row {row_num}: validation failed for ({', '.join(err['loc'])}).",
                                    "details": f"{err['msg']}. You passed `{err['input']}`",
                                }
                            )
                    except RepositoryError as e:
                        logger.error(str(e))
                        errs.append(f"Repo error row num {row_num}")
                    except Exception as e:
                        logger.error(str(e))
                        # TODO: Resulting errors exposes too much. Wrap in safe handler.
                        errs.append(f"Unexpected error while importing row {row_num}")

            # Update file status
            status = (
                TransactionsFileImportStatus.IMPORTED.value
                if not errs
                else TransactionsFileImportStatus.FAILED.value
            )
            await self.file_repo.update_by_id(file_record.id, {"status": status})
        except Exception as e:
            errs.append(f"File processing error: {str(e)}")

        return {
            "errors": errs,
            "messages": messages,
            "warnings": warns,
            "num_imported": len(messages),
            "num_skipped": len(warns),
            "num_failed": len(errs),
        }

    async def get_user_files(self, user: User) -> List[TransactionsFile]:
        """
        List all files for a user.
        """

        return user.transactions_files

    async def get_file_metadata(self, file_id: UUID) -> TransactionsFileSchema:
        """
        Get metadata for a specific file.
        """
        file_record = await self.file_repo.get_by_id(file_id)

        logger.debug(file_record.preview_data)
        logger.debug(type(file_record.preview_data))
        if not file_record:
            raise ServiceError("File record not found.")
        return TransactionsFileSchema.model_validate(file_record)

    async def _validate_csv(self, file: UploadFile | None) -> bool:
        return await self.file_service.is_csv(file)

    async def fetch_by_id(self, transaction_file_id: UUID) -> TransactionsFile:
        """
        Fetch a transaction file by its ID.

        Args:
            transaction_file_id (UUID): The transaction file ID to fetch.

        Returns:
            TransactionsFile: The transaction file object.

        Raises:
            ServiceError: If the file is not found.
        """
        try:
            file = await self.file_repo.get_by_id(transaction_file_id)
        except ResourceNotFound as e:
            raise ServiceError(str(e)) from e
        return file
