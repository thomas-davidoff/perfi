from perfi.core.database import User
from .faker import faker


class UserFactory:
    @staticmethod
    async def create(session, **kwargs):
        user = User(
            username=kwargs.get("username", faker.user_name()),
            email=kwargs.get("email", faker.email()),
            password=kwargs.get("password", faker.password(length=9)),
        )
        session.add(user)
        await session.flush()
        return user
