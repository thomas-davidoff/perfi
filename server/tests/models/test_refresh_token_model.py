import pytest
from sqlalchemy.exc import IntegrityError
from app.models import RefreshToken, User
from app.models.refresh_token import (
    RefreshTokenSchema,
    RefreshTokenCreateSchema,
    RefreshTokenUpdateSchema,
)
import uuid
from datetime import datetime, timedelta, timezone


class TestRefreshToken:
    @pytest.fixture
    async def user(self, session):
        user = User(
            username="token_user",
            email="token_test@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()
        return user

    async def test_create_refresh_token_from_schema(self, session, user):
        expiry = datetime.now(timezone.utc) + timedelta(days=7)
        token_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="test_token_12345",
            expires_at=expiry,
            device_info="Test Browser on Windows",
        )

        token = RefreshToken(**token_data.model_dump())
        session.add(token)
        await session.flush()

        assert isinstance(token.uuid, uuid.UUID)
        assert isinstance(token.created_at, datetime)
        assert token.updated_at is None
        assert token.user_id == user.uuid
        assert token.token_value == "test_token_12345"
        assert token.expires_at == expiry
        assert token.last_used_at is None
        assert token.device_info == "Test Browser on Windows"
        assert token.revoked is False
        assert token.revoked_at is None

    async def test_token_requires_user(self, session):
        expiry = datetime.now(timezone.utc) + timedelta(days=7)
        token_data = RefreshTokenCreateSchema(
            token_value="test_token_12345", expires_at=expiry, user_id=uuid.uuid4()
        )

        token = RefreshToken(**token_data.model_dump(exclude={"user_id"}))
        session.add(token)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_token_requires_value(self, session, user):
        expiry = datetime.now(timezone.utc) + timedelta(days=7)
        token_data = RefreshTokenCreateSchema(
            user_id=user.uuid, expires_at=expiry, token_value="askjdn"
        )

        token = RefreshToken(**token_data.model_dump(exclude={"token_value"}))
        session.add(token)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_token_requires_expiry(self, session, user):
        token_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="test_token_12345",
            expires_at=datetime.now(timezone.utc),
        )

        token = RefreshToken(**token_data.model_dump(exclude={"expires_at"}))
        session.add(token)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_token_unique_value(self, session, user):
        expiry = datetime.now(timezone.utc) + timedelta(days=7)

        # Create first token
        token1_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="same_token_value",
            expires_at=expiry,
        )

        token1 = RefreshToken(**token1_data.model_dump())
        session.add(token1)
        await session.flush()

        # Try to create second token with same value
        token2_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="same_token_value",
            expires_at=expiry,
        )

        token2 = RefreshToken(**token2_data.model_dump())
        session.add(token2)
        with pytest.raises(IntegrityError, match="unique constraint"):
            await session.flush()

    async def test_token_update_with_schema(self, session, user):
        expiry = datetime.now(timezone.utc) + timedelta(days=7)
        token_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="test_token_12345",
            expires_at=expiry,
        )

        token = RefreshToken(**token_data.model_dump())
        session.add(token)
        await session.flush()

        initial_created_at = token.created_at
        assert token.updated_at is None
        assert token.last_used_at is None
        assert token.revoked is False

        # Update token with schema - mark as used
        now = datetime.now(timezone.utc)
        update_data = RefreshTokenUpdateSchema(last_used_at=now)

        # Apply updates from schema to model
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(token, field, value)

        session.add(token)
        await session.flush()

        assert token.last_used_at == now
        assert isinstance(token.updated_at, datetime)
        assert token.updated_at > initial_created_at
        assert token.created_at == initial_created_at

        # Revoke token
        revoke_data = RefreshTokenUpdateSchema(revoked=True, revoked_at=now)

        # Apply updates from schema to model
        for field, value in revoke_data.model_dump(exclude_unset=True).items():
            setattr(token, field, value)

        session.add(token)
        await session.flush()

        assert token.revoked is True
        assert token.revoked_at == now
        assert token.updated_at > initial_created_at

    def test_schema_validation(self):
        # Verify schema validation works
        user_id = uuid.uuid4()
        expiry = datetime.now(timezone.utc) + timedelta(days=7)

        token_schema = RefreshTokenSchema(
            uuid=uuid.uuid4(),
            user_id=user_id,
            token_value="test_schema_token",
            expires_at=expiry,
            created_at=datetime.now(timezone.utc),
        )

        # Convert to and from dict should preserve values
        token_dict = token_schema.model_dump()
        token_schema2 = RefreshTokenSchema(**token_dict)
        assert token_schema.user_id == token_schema2.user_id
        assert token_schema.token_value == token_schema2.token_value
        assert token_schema.expires_at == token_schema2.expires_at

    def test_repr(self):
        user_id = uuid.uuid4()
        token = RefreshToken(
            user_id=user_id,
            token_value="test_token",
            expires_at=datetime.now(timezone.utc),
        )
        assert repr(token) == f"<RefreshToken user_id={user_id}>"
