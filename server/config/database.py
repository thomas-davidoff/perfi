from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_settings
from sqlalchemy.engine.url import URL


settings = get_settings()

COMMON_DB_KWARGS = {
    "username": settings.DB_USER,
    "password": settings.DB_PASS,
    "host": settings.DB_HOST,
    "port": settings.DB_PORT,
    "database": settings.DB_NAME,
}

async_config = {**COMMON_DB_KWARGS, "drivername": "postgresql+asyncpg"}
sync_config = {**COMMON_DB_KWARGS, "drivername": "postgresql+psycopg2"}

DATABASE_URL_ASYNC = URL.create(**async_config)
DATABASE_URL_SYNC = URL.create(**sync_config)
