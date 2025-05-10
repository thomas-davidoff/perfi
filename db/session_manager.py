import contextlib
from collections.abc import AsyncGenerator, AsyncIterator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import logging

logger = logging.getLogger(__name__)


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self.locked = False

    def init(self, db_url: URL, lock: bool = True) -> None:

        if self.locked:
            logger.warning(
                "DatabaseSessionManager cannot be initialized twice, unless init() is run with strict mode off."
            )
            return

        connect_args = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }

        self._engine = create_async_engine(
            url=db_url, pool_pre_ping=True, connect_args=connect_args, echo=False
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

        if lock:
            self.locked = True

    async def close(self) -> None:
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise


db_manager = DatabaseSessionManager()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.session() as session:
        yield session
