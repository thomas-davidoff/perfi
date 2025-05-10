from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.transaction import TransactionRepository
from app.schemas import TransactionCreateSchema
from app.exc import IntegrityConflictException, UserExistsException
from pydantic import EmailStr, TypeAdapter


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
