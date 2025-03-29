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

        token1_data = RefreshTokenCreateSchema(
            user_id=user.uuid,
            token_value="same_token_value",
            expires_at=expiry,
        )

        token1 = RefreshToken(**token1_data.model_dump())
        session.add(token1)
        await session.flush()

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

        now = datetime.now(timezone.utc)
        update_data = RefreshTokenUpdateSchema(last_used_at=now)

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(token, field, value)

        session.add(token)
        await session.flush()

        assert token.last_used_at == now
        assert isinstance(token.updated_at, datetime)
        assert token.updated_at > initial_created_at
        assert token.created_at == initial_created_at

        revoke_data = RefreshTokenUpdateSchema(revoked=True, revoked_at=now)

        for field, value in revoke_data.model_dump(exclude_unset=True).items():
            setattr(token, field, value)

        session.add(token)
        await session.flush()

        assert token.revoked is True
        assert token.revoked_at == now
        assert token.updated_at > initial_created_at

    def test_schema_validation(self):
        user_id = uuid.uuid4()
        expiry = datetime.now(timezone.utc) + timedelta(days=7)

        token_schema = RefreshTokenSchema(
            uuid=uuid.uuid4(),
            user_id=user_id,
            token_value="test_schema_token",
            expires_at=expiry,
            created_at=datetime.now(timezone.utc),
        )

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
