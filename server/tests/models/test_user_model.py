import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User
import uuid
from datetime import datetime
from app.models.user import UserSchema, User


class TestUser:
    async def test_create_user(self, session):
        user_schema = UserSchema(
            username="test", email="test", hashed_password=b"Not a real hash"
        )
        user = User(**user_schema.model_dump())
        session.add(user)
        await session.flush()

        assert isinstance(user.uuid, uuid.UUID)
        assert isinstance(user.created_at, datetime)
        assert user.updated_at is None
        assert user.username == "test"
        assert user.email == "test"
        assert user.hashed_password == b"Not a real hash"
        assert user.is_active is True

    async def test_unique_username(self, session):
        user_data = UserSchema(
            username="test", email="test", hashed_password=b"Not a real hash"
        ).model_dump()
        user = User(**user_data)

        session.add(user)
        await session.flush()

        user2 = User(**{**user_data, **{"email": "another email"}})
        session.add(user2)
        with pytest.raises(
            IntegrityError,
            match='duplicate key value violates unique constraint "user_username_key"',
        ):
            await session.flush()

    async def test_unique_email(self, session):
        user_data = UserSchema(
            username="test", email="test", hashed_password=b"Not a real hash"
        ).model_dump()
        user = User(**user_data)

        session.add(user)
        await session.flush()

        user2 = User(**{**user_data, **{"username": "another username"}})
        session.add(user2)
        with pytest.raises(
            IntegrityError,
            match='duplicate key value violates unique constraint "user_email_key"',
        ):
            await session.flush()

    async def test_update_user(self, session):
        user_data = UserSchema(
            username="test_username", email="test", hashed_password=b"Not a real hash"
        ).model_dump()
        user = User(**user_data)

        session.add(user)
        await session.flush()

        initial_created_at = user.created_at
        assert user.updated_at is None
        user.username = "New username"

        session.add(user)
        await session.flush()
        assert isinstance(user.updated_at, datetime)

        assert user.updated_at > initial_created_at
        assert user.created_at == initial_created_at

    def test_repr(self):
        user = User(
            **UserSchema(
                username="test", email="test@example.com", hashed_password="test"
            ).model_dump()
        )
        assert repr(user) == f"<User username=test email=test@example.com active=True>"
