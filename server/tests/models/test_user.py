# from app.models import User
# import pytest
# import uuid
# from datetime import datetime

# from tests


# TEST_PASSWORD = "some test password"
# TEST_USERNAME = "testuser"
# TEST_EMAIL = "test@example.com"


# @pytest.fixture
# def user():
#     return User(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD)


# # This tests basemodel implementation
# async def test_user_id_creation(session, user):
#     """Test that a user gets a UUID automatically after being added to the session."""
#     assert user.id is None
#     session.add(user)
#     await session.flush()
#     assert isinstance(user.id, uuid.UUID)


# # This tests basemodel implementation
# async def test_user_has_created_at_timestamp(session, user):
#     """Test that a user gets a created_at timestamp automatically after being added to the session."""
#     assert user.created_at is None
#     session.add(user)
#     await session.flush()
#     assert isinstance(user.created_at, datetime)


# # This tests basemodel implementation
# async def test_user_has_updated_at_timestamp(session, user):
#     """Test that a user gets an updated_at timestamp automatically after being added to the session."""
#     assert user.updated_at is None
#     session.add(user)
#     await session.flush()
#     assert user.updated_at is None
#     user.email = "something else"
#     session.add(user)
#     await session.flush()
#     await session.refresh(user)
#     assert isinstance(user.updated_at, datetime)


# # This tests basemodel implementation
# def test_user_cannot_update_created_at():
#     """Test that a user cannot update created_at"""
#     user = User(username="testuser", email="test@example.com")

#     with pytest.raises(AttributeError):
#         user.created_at = "Something else"


# # This tests basemodel implementation
# def test_user_cannot_update_updated_at():
#     """Test that a user cannot update updated_at"""
#     user = User(username="testuser", email="test@example.com")

#     with pytest.raises(AttributeError):
#         user.updated_at = "Something else"


# def test_user_verify_password(user):
#     assert user.verify_password(TEST_PASSWORD) is True
#     assert user.verify_password("incorrect pass") is False


import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from tests.factories.user import UserFactory
import uuid
from datetime import datetime


class TestUser:

    TEST_USERNAME = "test_user"
    TEST_PASSWORD = "somesecurepassword"
    TEST_EMAIL = "test@example.com"

    TEST_USER = UserFactory.create(
        username=TEST_USERNAME, password=TEST_PASSWORD, email=TEST_EMAIL
    )

    def test_password_write_only(self):
        with pytest.raises(AttributeError, match="Password is write-only."):
            password = self.TEST_USER.password

    def test_password_hashing(self):
        assert self.TEST_USER._password_hash != self.TEST_PASSWORD.encode("utf-8")

        assert self.TEST_USER.verify_password(self.TEST_PASSWORD) is True
        assert self.TEST_USER.verify_password("wrongpassword") is False

    def test_timestamp_immutability(self):

        with pytest.raises(AttributeError, match="created_at is read-only"):
            self.TEST_USER.created_at = "something"

        with pytest.raises(AttributeError, match="updated_at is read-only"):
            self.TEST_USER.updated_at = "something"

    def test_user_repr(self):
        assert repr(self.TEST_USER) == f"<User {self.TEST_USERNAME}>"

    async def test_create_user(self, session):
        session.add(self.TEST_USER)
        await session.flush()

        # should have a UUID id
        assert isinstance(self.TEST_USER.id, uuid.UUID)

        # should have correct attributes
        assert self.TEST_USER.username == self.TEST_USERNAME
        assert self.TEST_USER.email == self.TEST_EMAIL

        # should have created_at timestamp
        assert self.TEST_USER.created_at is not None
        assert isinstance(self.TEST_USER.created_at, datetime)

        # prior to updates, should be None
        assert self.TEST_USER.updated_at is None

    async def test_unique_constraints(self, session):
        session.add(self.TEST_USER)
        await session.flush()
        async with session.begin_nested():
            with pytest.raises(IntegrityError):
                user2 = User(
                    username=self.TEST_USERNAME,
                    email="different_email",
                )
                session.add(user2)
                await session.flush()

        async with session.begin_nested():
            with pytest.raises(IntegrityError):
                user2 = User(
                    username="different username",
                    email=self.TEST_EMAIL,
                )
                session.add(user2)
                await session.flush()

    async def test_timestamp_update(self, session):
        user = UserFactory.create()
        session.add(user)
        await session.flush()

        initial_created_at = user.created_at

        assert user.updated_at is None

        user.username = self.TEST_USERNAME

        session.add(user)
        await session.flush()
        await session.refresh(user)

        assert user.updated_at is not None

        assert user.created_at == initial_created_at
