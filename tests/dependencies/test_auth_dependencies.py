import pytest
from unittest.mock import MagicMock
from uuid import uuid4, UUID
import jwt
from datetime import datetime, timezone, timedelta

from app.dependencies.auth import get_current_user, get_current_active_user
from app.services.auth import TokenData
from app.models import User
from app.exc import InvalidTokenException, InactiveUserException
from config.settings import settings
from app.repositories.user import UserRepository


class TestGetCurrentUser:
    """Test suite for get_current_user dependency function"""

    @pytest.fixture
    def valid_token(self, user):
        """Create a valid JWT token"""
        expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
        payload = {"sub": str(user.uuid), "exp": expiry}
        return jwt.encode(payload, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO)

    async def test_get_current_user_success(self, mocker, session, user, valid_token):
        """Test successful user retrieval with valid token"""
        # Mock UserRepository.get_one_by_id to return our mock user
        mock_get_user = mocker.patch.object(
            UserRepository, "get_one_by_id", return_value=user
        )

        # Call the function
        result = await get_current_user(token=valid_token, session=session)

        # Assertions
        assert result == user
        mock_get_user.assert_called_once()
        # Verify the UUID was properly parsed
        call_args = mock_get_user.call_args[0]
        assert isinstance(call_args[1], UUID)
        assert str(call_args[1]) == str(user.uuid)

    async def test_get_current_user_invalid_token_format(self, session):
        """Test with malformed JWT token"""
        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token="invalid.token.format", session=session)

    async def test_get_current_user_missing_subject(self, mocker, session):
        """Test with token missing 'sub' claim"""
        # Create token without 'sub' claim
        payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        token = jwt.encode(
            payload, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO
        )

        with pytest.raises(InvalidTokenException, match="Token missing subject claim"):
            await get_current_user(token=token, session=session)
            # pass

    async def test_get_current_user_expired_token(self, mocker, session, user: User):
        """Test with expired JWT token"""
        # Create expired token
        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired
        }
        expired_token = jwt.encode(
            payload, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO
        )

        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token=expired_token, session=session)

    async def test_get_current_user_wrong_secret(self, mocker, session, user):
        """Test with token signed with wrong secret"""
        # Create token with wrong secret
        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        wrong_token = jwt.encode(
            payload, "wrong_secret_key", algorithm=settings.jwt.ALGO
        )

        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token=wrong_token, session=session)

    async def test_get_current_user_wrong_algorithm(self, mocker, session, user):
        """Test with token using wrong algorithm"""
        # Create token with wrong algorithm
        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        wrong_algo_token = jwt.encode(
            payload, settings.jwt.SECRET_KEY, algorithm="HS512"  # Wrong algorithm
        )

        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token=wrong_algo_token, session=session)

    async def test_get_current_user_not_found(self, mocker, session, valid_token):
        """Test when user doesn't exist in database"""
        # Mock UserRepository.get_one_by_id to return None
        mock_get_user = mocker.patch.object(
            UserRepository, "get_one_by_id", return_value=None
        )

        with pytest.raises(InvalidTokenException, match="User not found"):
            await get_current_user(token=valid_token, session=session)

        mock_get_user.assert_called_once()

    async def test_get_current_user_database_exception(
        self, mocker, session, valid_token
    ):
        """Test when database operation raises exception"""
        mock_get_user = mocker.patch.object(
            UserRepository, "get_one_by_id", side_effect=Exception("Database error")
        )

        with pytest.raises(InvalidTokenException, match="Failed to fetch user"):
            await get_current_user(token=valid_token, session=session)

        mock_get_user.assert_called_once()

    async def test_get_current_user_invalid_uuid_format(self, mocker, session):
        """Test with invalid UUID format in token"""
        # Create token with invalid UUID
        payload = {
            "sub": "not-a-valid-uuid",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        invalid_uuid_token = jwt.encode(
            payload, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO
        )

        with pytest.raises(InvalidTokenException, match="Invalid user ID format"):
            await get_current_user(token=invalid_uuid_token, session=session)


class TestGetCurrentActiveUser:
    """Test suite for get_current_active_user dependency function"""

    @pytest.fixture
    def active_user(self):
        """Create an active user mock"""
        user = MagicMock(spec=User)
        user.uuid = uuid4()
        user.email = "active@example.com"
        user.is_active = True
        return user

    @pytest.fixture
    def inactive_user(self):
        """Create an inactive user mock"""
        user = MagicMock(spec=User)
        user.uuid = uuid4()
        user.email = "inactive@example.com"
        user.is_active = False
        return user

    async def test_get_current_active_user_success(self, active_user):
        """Test successful retrieval of active user"""
        result = await get_current_active_user(current_user=active_user)
        assert result == active_user

    async def test_get_current_active_user_inactive(self, inactive_user):
        """Test with inactive user"""
        with pytest.raises(InactiveUserException, match="Inactive user"):
            await get_current_active_user(current_user=inactive_user)

    @pytest.mark.parametrize("is_active", [True, False])
    async def test_get_current_active_user_parametrized(self, is_active):
        """Parametrized test to cover both active and inactive cases"""
        user = MagicMock(spec=User)
        user.is_active = is_active

        if is_active:
            result = await get_current_active_user(current_user=user)
            assert result == user
        else:
            with pytest.raises(InactiveUserException):
                await get_current_active_user(current_user=user)


class TestGetCurrentUserEdgeCases:
    """Test edge cases and error conditions"""

    async def test_get_current_user_none_token(self, session):
        """Test with None token"""
        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token=None, session=session)

    async def test_get_current_user_empty_string_token(self, session):
        """Test with empty string token"""
        with pytest.raises(InvalidTokenException, match="Invalid token"):
            await get_current_user(token="", session=session)

    async def test_get_current_user_with_extra_claims(self, mocker, session, user):
        """Test with token containing extra claims (should still work)"""
        # Create token with extra claims
        payload = {
            "sub": str(user.uuid),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "extra_claim": "some_value",
            "role": "admin",
        }
        token_with_extras = jwt.encode(
            payload, settings.jwt.SECRET_KEY, algorithm=settings.jwt.ALGO
        )

        # Mock UserRepository.get_one_by_id
        mock_get_user = mocker.patch.object(
            UserRepository, "get_one_by_id", return_value=user
        )

        result = await get_current_user(token=token_with_extras, session=session)
        assert result == user


class TestGetCurrentUserIntegration:
    """Integration tests that use actual JWT encoding/decoding"""

    async def test_full_jwt_flow(self, mocker, session, user):
        """Test the full JWT flow from creation to validation"""
        token_data = TokenData(sub=user.uuid)
        token = jwt.encode(
            token_data.model_dump(),
            settings.jwt.SECRET_KEY,
            algorithm=settings.jwt.ALGO,
        )
        mock_get_user = mocker.patch.object(
            UserRepository, "get_one_by_id", return_value=user
        )

        result = await get_current_user(token=token, session=session)

        assert result == user
        mock_get_user.assert_called_once_with(session, user.uuid)
