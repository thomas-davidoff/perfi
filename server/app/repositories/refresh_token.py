from datetime import datetime, timezone
from uuid import UUID
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    RefreshToken,
    RefreshTokenSchema,
    RefreshTokenCreateSchema,
    RefreshTokenUpdateSchema,
)
from app.repositories.base import RepositoryFactory
from app.exc import NotFoundException

from config.settings import settings


class RefreshTokenRepository(RepositoryFactory(RefreshToken)):

    @classmethod
    async def generate_token(
        cls,
        session: AsyncSession,
        user_id: UUID,
        device_info: str = None,
    ) -> RefreshToken:
        """Generate a new refresh token for the specified user."""
        token_value = secrets.token_hex(32)  # 64 characters hex string
        expires_at = (
            datetime.now(timezone.utc) + settings.refresh_token_expires_in_minutes
        )

        token_data = RefreshTokenCreateSchema(
            user_id=user_id,
            token_value=token_value,
            expires_at=expires_at,
            device_info=device_info,
        )

        return await cls.create(session, data=token_data)

    @classmethod
    async def get_by_token_value(
        cls, session: AsyncSession, token_value: str
    ) -> RefreshToken:
        """Retrieve a refresh token by its value."""
        query = select(RefreshToken).where(RefreshToken.token_value == token_value)
        result = await session.execute(query)
        token = result.unique().scalar_one_or_none()

        if not token:
            raise NotFoundException(f"Refresh token not found.")

        return token

    @classmethod
    async def mark_as_used(cls, session: AsyncSession, token_id: UUID) -> RefreshToken:
        """Mark a token as used by updating its last_used_at timestamp."""
        update_data = RefreshTokenUpdateSchema(last_used_at=datetime.now(timezone.utc))
        return await cls.update_by_id(session, id_=token_id, data=update_data)

    @classmethod
    async def revoke_token(cls, session: AsyncSession, token_id: UUID) -> RefreshToken:
        """Revoke a refresh token."""
        update_data = RefreshTokenUpdateSchema(
            revoked=True, revoked_at=datetime.now(timezone.utc)
        )
        return await cls.update_by_id(session, id_=token_id, data=update_data)

    @classmethod
    async def revoke_all_for_user(cls, session: AsyncSession, user_id: UUID) -> int:
        """Revoke all tokens for a specific user."""
        tokens = await cls.get_active_tokens_for_user(session, user_id)

        for token in tokens:
            await cls.revoke_token(session, token.uuid)

        return len(tokens)

    @classmethod
    async def get_active_tokens_for_user(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[RefreshToken]:
        """Get all active (non-revoked, non-expired) tokens for a user."""
        now = datetime.now(timezone.utc)
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > now,
        )

        result = await session.execute(query)
        return result.unique().scalars().all()

    @classmethod
    async def cleanup_expired_tokens(cls, session: AsyncSession) -> int:
        """Remove all expired tokens from the database."""
        now = datetime.now(timezone.utc)
        query = select(RefreshToken).where(
            (RefreshToken.expires_at < now) | (RefreshToken.revoked == True)
        )

        result = await session.execute(query)
        tokens = result.unique().scalars().all()

        for token in tokens:
            await cls.remove_by_id(session, token.uuid)

        return len(tokens)
