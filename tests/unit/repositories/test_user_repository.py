import pytest
from app.exc import IntegrityConflictException
from app.repositories import UserRepository
from app.models import UserUpdateSchema, UserCreateSchema
from unittest.mock import MagicMock
from tests.utils import faker


class TestUserRepository:
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
        user = await UserRepository.create(session, test_user)
        assert user.uuid is not None
        assert user.created_at is not None
        assert user.updated_at is None
        assert user.email == test_user.email
        assert user.is_active is True
        assert user.hashed_password == test_user.password[::-1].encode("utf-8")

    async def test_create_user_conflict_username(self, session):
        test_user = UserCreateSchema(
            email=faker.email(),
            password=faker.password(),
        )
        await UserRepository.create(session, test_user)

        with pytest.raises(IntegrityConflictException):
            await UserRepository.create(session, test_user)

    async def test_update_user(self, session):
        test_user = UserCreateSchema(
            email=faker.email(),
            password=faker.password(),
        )
        user = await UserRepository.create(session, test_user)

        user_update = await UserRepository.update_by_id(
            session,
            id_=user.uuid,
            data=UserUpdateSchema(password="new_password".encode("utf-8")),
        )
        assert user_update.email == test_user.email
        assert user.hashed_password == b"drowssap_wen"

    async def test_update_user_conflict(self, session):
        test_user = UserCreateSchema(
            email=faker.email(),
            password=faker.password(),
        )
        test_user2 = UserCreateSchema(
            email=faker.email(),
            password=faker.password(),
        )

        await UserRepository.create(session, test_user)
        await UserRepository.create(session, test_user2)

        with pytest.raises(IntegrityConflictException):
            _ = await UserRepository.update_by_id(
                session,
                id_=test_user2.email,
                column="email",
                data=UserUpdateSchema(email=test_user.email),
            )
