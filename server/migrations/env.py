from alembic import context
from perfi.core.database import Base
import logging
from config import get_database_urls
from config.database import configure_alembic

DATABASE_URL_ASYNC, DATABASE_URL_SYNC = get_database_urls()


target_metadata = Base.metadata


msg = f"Registered tables: {list(Base.metadata.tables.keys())}"

logger = logging.getLogger("migrations")
logger.debug("configuring alembic")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    _, script, engine = configure_alembic()

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline mode not implemented while in local dev...")
else:
    run_migrations_online()
