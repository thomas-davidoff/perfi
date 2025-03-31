from unittest import mock
from app.services import UserService
from app.models import UserCreateSchema, User
from unittest.mock import MagicMock
from app.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.exc import IntegrityConflictException, NotFoundException, UserExistsException
import pytest


mock_session = MagicMock()


class TestUserService:
    async def test_create_user_success(self, mocker):
        """Test that UserService.create_user successfully creates a user"""
        # Arrange
        mock_session = MagicMock()
        test_user_data = UserCreateSchema(
            email="test@example.com", password="password123"
        )
        mock_user = MagicMock(spec=User)
        mock_user.uuid = "test-uuid"
        mock_user.email = "test@example.com"

        # Mock get_by_email to return None (user doesn't exist)
        mocker.patch.object(UserRepository, "get_by_email", return_value=None)

        # Create the mock for UserRepository.create
        mock_create = mocker.patch.object(
            UserRepository, "create", return_value=mock_user
        )

        # Act
        result = await UserService.create_user(
            session=mock_session, user_data=test_user_data
        )

        # Assert
        mock_create.assert_called_once_with(session=mock_session, data=test_user_data)
        assert result == mock_user
        assert result.email == "test@example.com"

    async def test_create_user_exists_by_email(self, mocker):
        """Test that UserService.create_user handles existing user by email"""
        # Arrange
        mock_session = MagicMock()
        test_user_data = UserCreateSchema(
            email="test@example.com", password="password123"
        )

        # Mock get_by_email to return an existing user
        mock_existing_user = MagicMock(spec=User)
        mocker.patch.object(
            UserRepository, "get_by_email", return_value=mock_existing_user
        )

        # Mock for UserRepository.create (should not be called)
        mock_create = mocker.patch.object(UserRepository, "create")

        # Act & Assert
        with pytest.raises(UserExistsException) as exc_info:
            await UserService.create_user(
                session=mock_session, user_data=test_user_data
            )

        assert f"User with email {test_user_data.email} already exists" in str(
            exc_info.value
        )
        mock_create.assert_not_called()

    async def test_create_user_integrity_error(self, mocker):
        """Test that UserService.create_user handles repository integrity errors"""
        # Arrange
        mock_session = MagicMock()
        test_user_data = UserCreateSchema(
            email="test@example.com", password="password123"
        )

        # Mock get_by_email to return None (user doesn't exist)
        mocker.patch.object(UserRepository, "get_by_email", return_value=None)

        # Mock repository to raise an integrity exception
        mock_create = mocker.patch.object(
            UserRepository,
            "create",
            side_effect=IntegrityConflictException("Database integrity error"),
        )

        # Act & Assert
        with pytest.raises(UserExistsException) as exc_info:
            await UserService.create_user(
                session=mock_session, user_data=test_user_data
            )

        assert "Failed to create user" in str(exc_info.value)
        mock_create.assert_called_once_with(session=mock_session, data=test_user_data)

    @pytest.mark.parametrize(
        "email", ["test@subdomain.example.io", "test@example.com", "TEST@EXAMPLE.COM"]
    )
    async def test_find_user_by_email_success(self, mocker, email):
        mock_user = MagicMock(spec=User)
        mock_get_by_email = mocker.patch.object(
            UserRepository, "get_by_email", return_value=mock_user
        )
        result = await UserService.get_user_by_email(session=mock_session, email=email)
        # returns a User object
        assert isinstance(result, User)
        mock_get_by_email.assert_called_once_with(
            session=mock_session, email=email.lower()
        )

    async def test_find_user_by_email_not_found(self, mocker):
        email = "test@example.com"
        mock_get_by_email = mocker.patch.object(
            UserRepository, "get_by_email", return_value=None
        )
        result = await UserService.get_user_by_email(session=mock_session, email=email)
        # returns a User object
        assert result is None
        mock_get_by_email.assert_called_once_with(
            session=mock_session, email=email.lower()
        )
