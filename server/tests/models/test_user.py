import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from tests.factories.user import UserFactory
import uuid
from datetime import datetime
import tests.constants as C
from sqlalchemy.orm import selectinload


class TestUser:
    @pytest.fixture(scope="class")
    def t_user(self):
        return UserFactory.create(
            username=C.TEST_USERNAME,
            password=C.TEST_PASSWORD,
            email=C.TEST_EMAIL,
            bypass_hashing=False,
        )

    def test_password_write_only(self, t_user):
        with pytest.raises(AttributeError, match="Password is write-only."):
            password = t_user.password

    def test_password_hashing(self, t_user):
        assert t_user._password_hash != C.TEST_PASSWORD.encode("utf-8")

        assert t_user.verify_password(C.TEST_PASSWORD) is True
        assert t_user.verify_password("wrongpassword") is False

    def test_timestamp_immutability(self, t_user):

        with pytest.raises(AttributeError, match="created_at is read-only"):
            t_user.created_at = "something"

        with pytest.raises(AttributeError, match="updated_at is read-only"):
            t_user.updated_at = "something"

    def test_user_repr(self, t_user):
        assert repr(t_user) == f"<User {C.TEST_USERNAME}>"

    async def test_create_user(self, session, t_user):
        session.add(t_user)
        await session.flush()

        # should have a UUID id
        assert isinstance(t_user.id, uuid.UUID)

        # should have correct attributes
        assert t_user.username == C.TEST_USERNAME
        assert t_user.email == C.TEST_EMAIL

        # should have created_at timestamp
        assert t_user.created_at is not None
        assert isinstance(t_user.created_at, datetime)

        # prior to updates, should be None
        assert t_user.updated_at is None

    async def test_unique_constraints(self, session, t_user):
        session.add(t_user)
        await session.flush()
        async with session.begin_nested():
            with pytest.raises(IntegrityError):
                user2 = User(
                    username=C.TEST_USERNAME,
                    email="different_email",
                )
                session.add(user2)
                await session.flush()

        async with session.begin_nested():
            with pytest.raises(IntegrityError):
                user2 = User(
                    username="different username",
                    email=C.TEST_EMAIL,
                )
                session.add(user2)
                await session.flush()

    async def test_timestamp_update(self, session):
        user = UserFactory.create()
        session.add(user)
        await session.flush()

        initial_created_at = user.created_at

        assert user.updated_at is None

        user.username = C.TEST_USERNAME

        session.add(user)
        await session.flush()
        await session.refresh(user)

        assert user.updated_at is not None

        assert user.created_at == initial_created_at


class TestUserRelationships:
    """Tests for User relationships"""

    async def test_user_to_refresh_tokens(self, session, db_user, db_token):
        """Test accessing tokens from user"""
        query = (
            select(User)
            .options(selectinload(User.refresh_tokens))
            .where(User.id == db_user.id)
        )
        result = await session.execute(query)
        user = result.scalars().first()

        assert len(user.refresh_tokens) == 1
        assert user.refresh_tokens[0].id == db_token.id
