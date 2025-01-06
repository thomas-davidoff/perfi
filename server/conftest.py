from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from perfi.core.database import Base
import pytest_asyncio


@pytest_asyncio.fixture
async def engine():
    """Set up the database schema for the test session."""
    db_settings = {
        "user": "perfi_test",
        "password": "perfi_test_pass",
        "host": "test_db",
        "port": 5432,
        "dbname": "perfi_test",
    }

    url = (
        f"postgresql+asyncpg://{db_settings['user']}:{db_settings['password']}"
        f"@{db_settings['host']}:{db_settings['port']}/{db_settings['dbname']}"
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
