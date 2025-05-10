from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.transaction import TransactionRepository
from app.schemas import TransactionCreateSchema
from app.exc import IntegrityConflictException, UserExistsException
from pydantic import EmailStr, TypeAdapter
from app.services.accounts import AccountService


class TransactionService:
    @classmethod
    async def create_transaction(
        cls, session: AsyncSession, data: TransactionCreateSchema
    ):
        try:
            user = await TransactionRepository.create(session=session, data=data)
            return user
        except IntegrityConflictException as e:
            raise UserExistsException(f"Failed to create user: {str(e)}") from e

    @classmethod
    async def list_transactions(cls, session: AsyncSession, user_id: UUID):

        user_accounts = await AccountService.get_accounts_by_user_id(
            session=session, user_id=user_id
        )

        try:
            transactions = await TransactionRepository.get_many_by_ids(
                session=session,
                ids=[a.uuid for a in user_accounts],
                column="account_id",
            )
        except Exception as e:
            print(e)
        return transactions
