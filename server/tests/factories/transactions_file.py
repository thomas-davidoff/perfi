from perfi.models import TransactionsFileImportStatus, TransactionsFile
from .user import UserFactory
from .account import AccountFactory
from sqlalchemy.orm import selectinload
from sqlalchemy import select
import json


class TransactionsFileFactory:
    @staticmethod
    async def create(
        session,
        user=None,
        account=None,
        filename="test_file.csv",
        file_path="/path/to/test_file.csv",
        status=None,
        preview_data=None,
        mapped_headers=None,
        error_log=None,
        add_and_flush=True,
    ):
        if not user:
            user = await UserFactory.create(session=session)
        if not account:
            account = await AccountFactory.create(session=session, user=user)
        if not status:
            status = TransactionsFileImportStatus.PENDING

        kwargs = {
            "user_id": user.id,
            "account_id": account.id,
            "filename": filename,
            "file_path": file_path,
            "status": status,
        }

        if preview_data is not None:
            kwargs["preview_data"] = json.dumps(preview_data)
        if mapped_headers is not None:
            kwargs["mapped_headers"] = json.dumps(mapped_headers)
        if error_log is not None:
            kwargs["error_log"] = json.dumps(error_log)

        transactions_file = TransactionsFile(**kwargs)
        if not add_and_flush:
            return transactions_file

        session.add(transactions_file)
        await session.flush()

        stmt = (
            select(TransactionsFile)
            .where(TransactionsFile.id == transactions_file.id)
            .options(selectinload(TransactionsFile.transactions))
        )
        result = await session.execute(stmt)
        refreshed = result.scalars().first()

        return refreshed
