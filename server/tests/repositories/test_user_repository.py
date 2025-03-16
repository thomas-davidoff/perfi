import pytest
from app.exc import IntegrityConflictException
from app.repositories.user import UserCrud
from app.models import UserUpdateSchema, UserCreateSchema
from unittest.mock import MagicMock
from tests.utils import faker


class TestUserCrud:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        mock_function = MagicMock(side_effect=lambda x: x[::-1].encode("utf-8"))
        monkeypatch.setattr("app.repositories.user.hash_password", mock_function)

    async def test_create_user(self, session):
        test_user = UserCreateSchema(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )
        user = await UserCrud.create(session, test_user)
        assert user.uuid is not None
        assert user.created_at is not None
        assert user.updated_at is None
        assert user.username == test_user.username
        assert user.email == test_user.email
        assert user.is_active is True
        assert user.hashed_password == test_user.password[::-1].encode("utf-8")

    async def test_create_user_conflict_username(self, session):
        test_user = UserCreateSchema(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )
        await UserCrud.create(session, test_user)

        test_user.email = faker.email()

        with pytest.raises(IntegrityConflictException):
            await UserCrud.create(session, test_user)

    async def test_update_user(self, session):
        test_user = UserCreateSchema(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )
        user = await UserCrud.create(session, test_user)

        user_update = await UserCrud.update_by_id(
            session,
            id_=user.uuid,
            data=UserUpdateSchema(password="new_password".encode("utf-8")),
        )
        assert user_update.username == test_user.username
        assert user_update.email == test_user.email
        assert user.hashed_password == b"drowssap_wen"

    async def test_update_user_conflict(self, session):
        test_user = UserCreateSchema(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )
        test_user2 = UserCreateSchema(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )

        await UserCrud.create(
            session,
            test_user,
        )

        await UserCrud.create(session, test_user2)

        with pytest.raises(IntegrityConflictException):
            _ = await UserCrud.update_by_id(
                session,
                id_=test_user.username,
                column="username",
                data=UserUpdateSchema(email=test_user2.email),
            )
