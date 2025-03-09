from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.user import User
from app.models.refresh_token import RefreshToken


class TestRefreshToken:
    async def test_create_refresh_token(self, session, db_user):
        """Test that a refresh token can be created successfully and has the correct attributes"""
        token = RefreshToken(
            user_id=db_user.id, token_value="someval", device_info="somedeviceinfo"
        )
        session.add(token)
        await session.flush()

        # should have a UUID id
        assert token.id is not None
        assert isinstance(token.id, UUID)

        # should have created_at timestamp
        assert token.created_at is not None
        assert isinstance(token.created_at, datetime)

        # should NOT have updated_at
        assert token.updated_at is None

        # should have correct attributes
        assert token.token_value == "someval"
        assert token.user_id == db_user.id
        assert token.device_info == "somedeviceinfo"
        assert isinstance(token.expires_at, datetime)
        assert token.expires_at.strftime("%Y-%m-%d") == (
            datetime.now() + timedelta(days=7)
        ).strftime("%Y-%m-%d")

        assert token.revoked is False
        assert token.revoked_at is None
        assert token.last_used_at is None


class TestRefreshTokenRelationships:
    """Tests for RefreshToken relationships"""

    async def test_token_user_relationship(self, session, db_user, db_token):
        """Test accessing user from token"""

        query = (
            select(RefreshToken)
            .options(selectinload(RefreshToken.user))
            .where(RefreshToken.id == db_token.id)
        )
        result = await session.execute(query)
        token = result.scalars().first()

        assert isinstance(token.user, User)
        assert token.user.id == db_user.id
