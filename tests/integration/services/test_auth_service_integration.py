from unittest.mock import MagicMock
import pytest
from app.models.user import User
from app.services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import faker
from app.models import User, UserCreateSchema
from app.services import UserService, AuthService


mock_session = MagicMock(spec=AsyncSession)


TEST_USER_EMAIL = faker.email()
TEST_USER_PASSWORD = faker.password()


class TestAuthService:

    @pytest.fixture
    async def db_user(session):
        user = await UserService.create_user(
            session,
            UserCreateSchema(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD),
        )
        return user

    async def test_authenticate_user_success(self, session):

        user = await UserService.create_user(
            session,
            UserCreateSchema(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD),
        )

        user = await AuthService.authenticate_user(
            session=session, email=user.email, password=TEST_USER_PASSWORD
        )
        assert isinstance(user, User)
