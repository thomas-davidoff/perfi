from perfi.models import User
from .faker import faker
from sqlalchemy.orm import selectinload
from sqlalchemy import select


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
        stmt = (
            select(User).where(User.id == user.id).options(selectinload(User.accounts))
        )
        result = await session.execute(stmt)
        refreshed_user = result.scalars().first()

        return refreshed_user
