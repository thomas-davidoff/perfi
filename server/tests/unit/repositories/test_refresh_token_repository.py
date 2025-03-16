import pytest
from datetime import datetime, timedelta, timezone
from app.exc import IntegrityConflictException, NotFoundException
from app.repositories import RefreshTokenRepository
from app.models import RefreshTokenCreateSchema, RefreshTokenUpdateSchema
from tests.utils import faker
from uuid import uuid4
from config.settings import settings


class TestRefreshTokenCrud:
    async def test_create_refresh_token(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        test_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
            device_info="Test Device",
        )

        token = await RefreshTokenRepository.create(session, test_token)

        assert token.uuid is not None
        assert token.created_at is not None
        assert token.updated_at is None
        assert token.user_id == test_token.user_id
        assert token.token_value == test_token.token_value
        assert token.expires_at == test_token.expires_at
        assert token.device_info == test_token.device_info
        assert token.revoked is False
        assert token.revoked_at is None

    async def test_create_refresh_token_duplicate_value(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        token_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
        )

        # First token creation should succeed
        await RefreshTokenRepository.create(session, token_data)

        # Second token with same value should fail
        with pytest.raises(IntegrityConflictException):
            await RefreshTokenRepository.create(session, token_data)

    async def test_get_token_by_id(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        test_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
        )

        token = await RefreshTokenRepository.create(session, test_token)
        retrieved = await RefreshTokenRepository.get_one_by_id(session, token.uuid)

        assert retrieved is not None
        assert retrieved.uuid == token.uuid
        assert retrieved.token_value == token.token_value

    async def test_get_by_token_value(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        test_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
        )

        token = await RefreshTokenRepository.create(session, test_token)
        retrieved = await RefreshTokenRepository.get_by_token_value(
            session, token_value
        )

        assert retrieved is not None
        assert retrieved.uuid == token.uuid

    async def test_get_by_nonexistent_token_value(self, session):
        with pytest.raises(NotFoundException):
            await RefreshTokenRepository.get_by_token_value(
                session, "nonexistent_token"
            )

    async def test_mark_as_used(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        test_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
        )

        token = await RefreshTokenRepository.create(session, test_token)
        assert token.last_used_at is None

        updated = await RefreshTokenRepository.mark_as_used(session, token.uuid)
        assert updated.last_used_at is not None

    async def test_revoke_token(self, session, user):
        token_value = faker.uuid4()
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        test_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=token_value,
            expires_at=expires_at,
        )

        token = await RefreshTokenRepository.create(session, test_token)
        assert token.revoked is False
        assert token.revoked_at is None

        updated = await RefreshTokenRepository.revoke_token(session, token.uuid)
        assert updated.revoked is True
        assert updated.revoked_at is not None

    async def test_generate_token(self, session, user):
        device_info = "Test Device"
        token = await RefreshTokenRepository.generate_token(
            session, user.uuid, device_info
        )

        assert token.uuid is not None
        assert token.user_id == user.uuid
        assert token.token_value is not None
        assert len(token.token_value) == 64  # 32 bytes as hex = 64 chars
        assert token.expires_at > datetime.now(timezone.utc)
        assert token.device_info == device_info
        assert token.revoked is False

    async def test_get_active_tokens_for_user(self, session, user):
        # Create some active tokens
        for i in range(3):
            await RefreshTokenRepository.generate_token(session, user.uuid)

        # Create a revoked token
        token = await RefreshTokenRepository.generate_token(session, user.uuid)
        await RefreshTokenRepository.revoke_token(session, token.uuid)

        # Create an expired token
        expired_token = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value=faker.uuid4(),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        await RefreshTokenRepository.create(session, expired_token)

        active_tokens = await RefreshTokenRepository.get_active_tokens_for_user(
            session, user.uuid
        )
        assert len(active_tokens) == 3

    async def test_revoke_all_for_user(self, session, user):
        # Create some tokens
        for i in range(5):
            await RefreshTokenRepository.generate_token(session, user.uuid)

        count = await RefreshTokenRepository.revoke_all_for_user(session, user.uuid)
        assert count == 5

        active_tokens = await RefreshTokenRepository.get_active_tokens_for_user(
            session, user.uuid
        )
        assert len(active_tokens) == 0

    async def test_cleanup_expired_tokens(self, session, user):
        for i in range(2):
            await RefreshTokenRepository.generate_token(session, user.uuid)

        for i in range(3):
            expired_token = RefreshTokenCreateSchema(
                user_id=user.uuid,
                token_value=faker.uuid4(),
                expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            )
            await RefreshTokenRepository.create(session, expired_token)

        for i in range(2):
            token = await RefreshTokenRepository.generate_token(session, user.uuid)
            await RefreshTokenRepository.revoke_token(session, token.uuid)

        all_tokens_before = await RefreshTokenRepository.get_many_by_ids(session)
        assert len(all_tokens_before) >= 7  # At least our 7 tokens

        cleaned = await RefreshTokenRepository.cleanup_expired_tokens(session)
        assert cleaned == 5  # 3 expired + 2 revoked

        all_tokens_after = await RefreshTokenRepository.get_many_by_ids(session)
        assert len(all_tokens_after) == len(all_tokens_before) - 5
