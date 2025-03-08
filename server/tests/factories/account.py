from perfi.models import Account, AccountType
from .user import UserFactory
from .faker import faker
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class AccountFactory:
    @staticmethod
    async def create(
        session, user=None, name=None, account_type=None, add_and_flush=True
    ):
        """Create an Account with optional User, eagerly loading relationships."""
        if not user:
            user = await UserFactory.create(session=session)

        if name is None:
            name = faker.company()

        if account_type is None:
            account_type = AccountType.CHECKING

        account = Account(
            user_id=user.id,
            name=name,
            account_type=account_type,
        )
        if not add_and_flush:
            return account

        session.add(account)
        await session.flush()

        stmt = (
            select(Account)
            .where(Account.id == account.id)
            .options(selectinload(Account.user))
        )
        result = await session.execute(stmt)
        refreshed_account = result.scalars().first()

        return refreshed_account
