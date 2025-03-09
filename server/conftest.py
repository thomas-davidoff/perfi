import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from config import get_settings
import pytest
from app.models import BaseModel

# This is important!
# Creates a module-scoped event loop to be grabbed by the fixtures here
# https://github.com/pytest-dev/pytest-asyncio/discussions/587
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def init_db():
    settings = get_settings(environment="test")
    db_url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}"
        f"@{settings.DB_HOST}:{int(settings.DB_PORT)}/{settings.DB_NAME}"
    )
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(init_db):
    """Create a new session for each test function with its own transaction"""
    connection = await init_db.connect()

    transaction = await connection.begin()

    async_session = async_sessionmaker(
        expire_on_commit=False, class_=AsyncSession, bind=connection, autoflush=False
    )

    async with async_session() as session:
        yield session
        await session.close()

    await transaction.rollback()
    await connection.close()


from tests.factories import UserFactory
import tests.constants as C
from app.models import RefreshToken, Account, AccountType


@pytest.fixture
async def db_user(session):
    user = UserFactory.create(
        username=C.TEST_USERNAME,
        password=C.TEST_PASSWORD,
        email=C.TEST_EMAIL,
    )

    session.add(user)
    await session.flush()
    return user


@pytest.fixture
async def db_token(session, db_user):
    token = RefreshToken(user_id=db_user.id, token_value="someval")
    session.add(token)
    await session.flush()
    return token


@pytest.fixture
async def db_account(session, db_user):
    account = Account(
        user_id=db_user.id,
        name="Checking Account",
        account_type=AccountType.CHECKING,
        institution="Test Bank",
    )
    session.add(account)
    await session.flush()
    return account
