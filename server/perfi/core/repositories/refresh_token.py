from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid

from perfi.core.database import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: uuid.UUID, token: str, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id, token=token, expires_at=expires_at
        )
        self.session.add(refresh_token)
        await self.session.commit()
        return refresh_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        query = (
            select(RefreshToken)
            .where(RefreshToken.token == token)
            .options(joinedload(RefreshToken.user))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete(self, token: str) -> None:
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        refresh_token = result.scalars().first()
        if refresh_token:
            await self.session.delete(refresh_token)
            await self.session.commit()

    async def delete_expired(self) -> None:
        query = select(RefreshToken).where(
            RefreshToken.expires_at < datetime.now(datetime.timezone.utc)
        )
        result = await self.session.execute(query)
        for refresh_token in result.scalars().all():
            await self.session.delete(refresh_token)
        await self.session.commit()
