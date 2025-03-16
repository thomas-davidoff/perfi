from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.user import User
from app.models.refresh_token import RefreshToken
from tests.factories import RefreshTokenFactory, UserFactory


class TestRefreshToken:
    async def test_create_refresh_token(self, session):
        """Test that a refresh token can be created successfully and has the correct attributes"""
        user = await UserFactory.create(session)
        token = await RefreshTokenFactory.create(
            session,
            user=user,
            token_value="someval",
            device_info="somedeviceinfo",
            expires_at=datetime.now() + timedelta(days=7),
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
        assert token.user_id == user.id
        assert token.device_info == "somedeviceinfo"
        assert isinstance(token.expires_at, datetime)
        assert token.expires_at.strftime("%Y-%m-%d") == (
            datetime.now() + timedelta(days=7)
        ).strftime("%Y-%m-%d")

        assert token.revoked is False
        assert token.revoked_at is None
        assert token.last_used_at is None

    def test_repr(self):
        token = RefreshToken(
            user_id=123, token_value="someval", device_info="somedeviceinfo"
        )
        assert repr(token) == f"<RefreshToken user_id=123>"


class TestRefreshTokenRelationships:
    """Tests for RefreshToken relationships"""

    async def test_token_user_relationship(self, session):
        """Test accessing user from token"""

        user = await UserFactory.create(session)
        token = await RefreshTokenFactory.create(session, user=user)

        query = (
            select(RefreshToken)
            .options(selectinload(RefreshToken.user))
            .where(RefreshToken.id == token.id)
        )
        result = await session.execute(query)
        token = result.scalars().first()

        assert isinstance(token.user, User)
        assert token.user.id == user.id

    async def test_delete_user_deletes_refresh_token(self, session):
        token = await RefreshTokenFactory.create(session)
        query = (
            select(RefreshToken)
            .options(selectinload(RefreshToken.user))
            .where(RefreshToken.id == token.id)
        )
        before = await session.execute(query)
        assert before.scalars().first() is token

        await session.delete(token.user)
        await session.commit()

        after = await session.execute(query)
        assert after.scalars().first() is None
