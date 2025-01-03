from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from perfi.core.database import async_session_factory


# throw this one around as a db session that self-cleans
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an async database session with proper lifecycle management.
    """
    async with async_session_factory() as session:
        yield session
