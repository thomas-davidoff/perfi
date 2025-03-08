from perfi.models import Account
from .user import UserFactory
from .faker import faker


class AccountFactory:
    @staticmethod
    async def create(session, user=None, **kwargs):
        if not user:
            user = await UserFactory.create(session=session)
        account = Account(
            user_id=user.id,
            name=kwargs.get("name", faker.company()),
        )
        session.add(account)
        await session.flush()
        return account
