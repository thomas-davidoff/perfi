from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from app.exc import (
    InvalidCredentialsException,
    ExpiredTokenException,
    RevokedTokenException,
    RepositoryException,
    InvalidTokenException,
)
from app.repositories.refresh_token import RefreshTokenRepository
from app.services.auth import AuthService, TokenData, BearerAccessTokenRefreshTokenPair
from uuid import uuid4
import jwt
from app.services.user import UserService
from config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from pytest_mock import MockerFixture
from tests.utils import faker


mock_session = MagicMock(spec=AsyncSession)
mock_user_id = uuid4()


class TestTokenDataSchema:
    @pytest.mark.parametrize(
        "sub,exp", [[uuid4(), 123], [uuid4(), datetime.now(timezone.utc)]]
    )
    def test_model_serializes_correctly(self, sub, exp):
        data = TokenData(sub=sub, exp=exp)

        serialized_data = data.model_dump()
        assert isinstance(serialized_data["sub"], str)
        assert isinstance(serialized_data["exp"], datetime)


class TestAuthService:

    @pytest.fixture(scope="class")
    def mock_session(self):
        return MagicMock(spec=AsyncSession)

    class TestCreateAccessToken:
        @pytest.fixture(scope="class")
        def user_id(self):
            return uuid4()

        def decode_test_token(self, token):
            return jwt.decode(
                token, settings.jwt.SECRET_KEY, algorithms=[settings.jwt.ALGO]
            )

        async def test_returns_tuple(self, user_id):
            res = AuthService.create_access_token_for_user(user_id=user_id)
            assert isinstance(res, tuple)

        async def test_correctly_sets_subject(self, user_id):
            token, _ = AuthService.create_access_token_for_user(user_id=user_id)
            payload = self.decode_test_token(token)
            assert payload.get("sub") == str(user_id)

        async def test_sets_expiry_timestamp(self, user_id):
            token, expiry = AuthService.create_access_token_for_user(user_id=user_id)
            payload = self.decode_test_token(token)
            assert payload.get("exp") == expiry.replace(microsecond=0).timestamp()

        async def test_expiry_matches_app_settings(self, user_id):
            token, _ = AuthService.create_access_token_for_user(user_id=user_id)
            payload = self.decode_test_token(token)
            time_delta_minutes = payload.get("exp") - datetime.timestamp(
                datetime.now(timezone.utc)
            )

            assert (
                int(time_delta_minutes)
                == settings.jwt.ACCESS_TOKEN_EXPIRES_IN_MINUTES.total_seconds()
                - 1  # -1 here because there will always be at least a microsecond between the beginning of this function and the end. Still deterministic.
            )

    class TestAuthenticateUser:
        @pytest.fixture(scope="class")
        def mock_user(self):
            user = MagicMock()
            user.id = uuid4()
            user.email = "test@example.com"
            return user

        @pytest.fixture(scope="class")
        def mock_email(self):
            return faker.email()

        @pytest.fixture(autouse=True)
        def setup_mocks(self, monkeypatch):
            mock_function = MagicMock(
                side_effect=lambda self, x: x[::-1].encode("utf-8")
            )
            monkeypatch.setattr("app.services.auth.verify_password", mock_function)

        async def test_calls_out_to_user_service_to_get_user(
            self, mock_session, mocker: MockerFixture, mock_user
        ):
            mock_user_service_get_by_email = mocker.patch.object(
                UserService, "get_user_by_email", return_value=mock_user
            )

            await AuthService.authenticate_user(
                session=mock_session, email=mock_user.email, password="secret"
            )

            mock_user_service_get_by_email.assert_called_once_with(
                session=mock_session, email=mock_user.email
            )

        async def test_non_existent_user(
            self, mock_session, mocker: MockerFixture, mock_user
        ):
            mocker.patch.object(UserService, "get_user_by_email", return_value=None)

            with pytest.raises(InvalidCredentialsException):
                await AuthService.authenticate_user(
                    session=mock_session, email=mock_user.email, password="secret"
                )

        async def test_incorrect_password(
            self, mock_session, mocker: MockerFixture, mock_user
        ):
            mocker.patch.object(
                UserService, "get_user_by_email", return_value=mock_user
            )
            mocker.patch("app.services.auth.verify_password", return_value=False)

            with pytest.raises(InvalidCredentialsException):
                await AuthService.authenticate_user(
                    session=mock_session, email=mock_user.email, password="secret"
                )

    async def test_create_tokens_success(self, mocker: MockerFixture):
        user_id = uuid4()

        mock_create_access_token = mocker.patch.object(
            AuthService,
            "create_access_token_for_user",
            return_value=(
                "mock_access_token",
                datetime.now(timezone.utc) + timedelta(minutes=60),
            ),
        )

        mock_refresh_token = MagicMock()
        mock_refresh_token.token_value = "mock_refresh_token"
        mock_generate_token = mocker.patch.object(
            RefreshTokenRepository, "generate_token", return_value=mock_refresh_token
        )
        result = await AuthService.create_tokens(mock_session, user_id)

        mock_create_access_token.assert_called_once_with(user_id=user_id)
        mock_generate_token.assert_called_once_with(
            session=mock_session, user_id=user_id, device_info=None
        )

        assert isinstance(result, BearerAccessTokenRefreshTokenPair)
        assert result.token_type == "bearer"
        assert result.refresh_token == mock_refresh_token.token_value

    async def test_generate_new_access_token_from_refresh_token_success(self, mocker):
        """Test the happy path - valid token refreshes successfully."""
        refresh_token_value = "valid_token_value"
        mock_token = MagicMock()
        mock_token.user_id = uuid4()
        mock_token.revoked = False
        mock_token.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        mock_token.uuid = uuid4()

        mocker.patch.object(
            RefreshTokenRepository, "get_by_token_value", return_value=mock_token
        )

        mark_as_used_mock = mocker.patch.object(RefreshTokenRepository, "mark_as_used")

        expected_tokens = BearerAccessTokenRefreshTokenPair(
            access_token="new_access_token",
            token_type="bearer",
            refresh_token="new_refresh_token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        mocker.patch.object(AuthService, "create_tokens", return_value=expected_tokens)

        result = await AuthService.generate_new_access_token_from_refresh_token(
            mock_session, refresh_token_value
        )

        assert result == expected_tokens
        mark_as_used_mock.assert_called_once_with(mock_session, mock_token.uuid)

    async def test_generate_new_access_token_from_refresh_token_raises_revoked_token_error(
        self, mocker
    ):
        """Test that a revoked token raises the appropriate exception."""
        refresh_token_value = "revoked_token"

        mock_token = MagicMock()
        mock_token.revoked = True
        mock_token.expires_at = datetime.now(timezone.utc) + timedelta(days=1)

        mocker.patch.object(
            RefreshTokenRepository, "get_by_token_value", return_value=mock_token
        )

        with pytest.raises(RevokedTokenException, match="Token has been revoked"):
            await AuthService.generate_new_access_token_from_refresh_token(
                mock_session, refresh_token_value
            )

    async def test_generate_new_access_token_from_refresh_token_raises_expired_token_error(
        self, mocker
    ):
        """Test that an expired token raises the appropriate exception."""
        refresh_token_value = "expired_token"

        mock_token = MagicMock()
        mock_token.revoked = False
        mock_token.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        mocker.patch.object(
            RefreshTokenRepository, "get_by_token_value", return_value=mock_token
        )

        with pytest.raises(ExpiredTokenException, match="Token has expired"):
            await AuthService.generate_new_access_token_from_refresh_token(
                mock_session, refresh_token_value
            )

    async def test_generate_new_access_token_from_refresh_token_handles_repository_errors(
        self, mocker
    ):
        """Test handling of repository errors."""
        refresh_token_value = "invalid_token"

        mocker.patch.object(
            RefreshTokenRepository,
            "get_by_token_value",
            side_effect=RepositoryException("Database error"),
        )

        with pytest.raises(InvalidTokenException, match="Invalid refresh token"):
            await AuthService.generate_new_access_token_from_refresh_token(
                mock_session, refresh_token_value
            )

    async def test_logout_calls_out_to_repository_to_revoke_token(
        self, mocker: MockerFixture
    ):
        """
        logout accepts a refresh token value, finds the refresh token by its value, and revokes the token
        """

        mock_refresh_token = MagicMock()
        mock_refresh_token.token_value = "secret"

        mock_get_by_token_value = mocker.patch.object(
            RefreshTokenRepository,
            "get_by_token_value",
            return_value=mock_refresh_token,
        )
        mock_revoke_token = mocker.patch.object(
            RefreshTokenRepository,
            "revoke_token",
        )

        await AuthService.logout(
            session=mock_session, refresh_token_value=mock_refresh_token.token_value
        )

        mock_get_by_token_value.assert_awaited_once()
        mock_revoke_token.assert_awaited_once()
