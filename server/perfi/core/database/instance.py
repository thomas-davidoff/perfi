from config import get_database_urls
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL_ASYNC, DATABASE_URL_SYNC = get_database_urls()

engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)

async_session_factory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
