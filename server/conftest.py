from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from perfi.core.database import Base
import pytest
import pytest_asyncio
from config import get_settings, Settings


@pytest.fixture
def settings() -> Settings:
    # hardcode test env here to prevent accidentally using dev db
    return get_settings(environment="test")


@pytest_asyncio.fixture
async def engine(settings: Settings):

    url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}"
        f"@{settings.DB_HOST}:{int(settings.DB_PORT)}/{settings.DB_NAME}"
    )

    engine = create_async_engine(
        url,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide a transactional database session for each test."""
    TestSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()
