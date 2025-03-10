import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, Account, RefreshToken
from tests.factories import UserFactory, RefreshTokenFactory, AccountFactory
import uuid
from datetime import datetime
import tests.constants as C
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class TestUser:
    async def test_password_write_only(self):
        user = await UserFactory.create(add_to_db=False)
        with pytest.raises(AttributeError, match="Password is write-only."):
            password = user.password

    async def test_password_hashing(self):
        user = await UserFactory.create(
            bypass_hashing=False, password=C.TEST_PASSWORD, add_to_db=False
        )
        assert user._password_hash != C.TEST_PASSWORD.encode("utf-8")

        assert user.verify_password(C.TEST_PASSWORD) is True
        assert user.verify_password("wrongpassword") is False

    async def test_timestamp_immutability(self):
        user = await UserFactory.create(add_to_db=False)

        with pytest.raises(AttributeError, match="created_at is read-only"):
            user.created_at = "something"

        with pytest.raises(AttributeError, match="updated_at is read-only"):
            user.updated_at = "something"

    async def test_user_repr(self):
        user = await UserFactory.create(add_to_db=False)
        assert repr(user) == f"<User {user.username}>"

    async def test_create_user(self, session):
        user = await UserFactory.create(
            session=session, username=C.TEST_USERNAME, email=C.TEST_EMAIL
        )

        # should have a UUID id
        assert isinstance(user.id, uuid.UUID)

        # should have correct attributes
        assert user.username == C.TEST_USERNAME
        assert user.email == C.TEST_EMAIL

        # should have created_at timestamp
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

        # prior to updates, should be None
        assert user.updated_at is None

    async def test_unique_constraints(self, session):

        user = await UserFactory.create(
            session=session, username=C.TEST_USERNAME, email=C.TEST_EMAIL
        )
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
        user = await UserFactory.create(session=session)

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

    async def test_user_to_refresh_tokens(self, session):
        """Test accessing tokens from user"""

        user = await UserFactory.create(session)
        token = await RefreshTokenFactory.create(session, user=user)

        query = (
            select(User)
            .options(selectinload(User.refresh_tokens))
            .where(User.id == user.id)
        )
        result = await session.execute(query)
        user = result.scalars().first()

        assert len(user.refresh_tokens) == 1
        assert user.refresh_tokens[0].id == token.id

    async def test_user_to_accounts(self, session):
        """Test accessing accounts from user"""

        user = await UserFactory.create(session)
        account = await AccountFactory.create(session, user=user)
        query = (
            select(User).options(selectinload(User.accounts)).where(User.id == user.id)
        )
        result = await session.execute(query)
        user = result.scalars().first()

        assert len(user.accounts) == 1
        assert user.accounts[0].id == account.id

    async def test_delete_user_deletes_orphans(self, session):
        """
        Test that deleting the user also deletes the associated refresh tokens and accounts
        """

        user = await UserFactory.create(session)
        await AccountFactory.create(session, user=user)
        await RefreshTokenFactory.create(session, user=user)

        # populate account and token
        await session.refresh(user, ["accounts", "refresh_tokens"])

        accounts_query = select(Account).where(Account.user_id == user.id)
        tokens_query = select(RefreshToken).where(RefreshToken.user_id == user.id)

        accounts_result = await session.execute(accounts_query)
        tokens_result = await session.execute(tokens_query)

        assert len(accounts_result.scalars().all()) == 1
        assert len(tokens_result.scalars().all()) == 1

        await session.delete(user)
        await session.flush()

        accounts_result = await session.execute(accounts_query)
        tokens_result = await session.execute(tokens_query)

        assert len(accounts_result.scalars().all()) == 0
        assert len(tokens_result.scalars().all()) == 0
