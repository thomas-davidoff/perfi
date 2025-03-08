from perfi.models import Account, AccountType
from .user import UserFactory
from .faker import faker
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class AccountFactory:
    @staticmethod
    async def create(session, user=None, **kwargs):
        """Create an Account with optional User, eagerly loading relationships."""
        if not user:
            user = await UserFactory.create(session=session)

        account = Account(
            user_id=user.id,
            name=kwargs.get("name", faker.company()),
            account_type=AccountType.CHECKING,
        )
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
