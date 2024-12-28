from alembic import context
from sqlalchemy import engine_from_config, pool
from perfi.core.database import Base
import logging
from perfi.core.dependencies.settings import get_settings
from config import get_database_urls

DATABASE_URL_ASYNC, DATABASE_URL_SYNC = get_database_urls(get_settings())


target_metadata = Base.metadata


msg = f"Registered tables: {list(Base.metadata.tables.keys())}"

logger = logging.getLogger("migrations")
logger.debug("configuring alembic")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": str(DATABASE_URL_SYNC)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline mode not implemented while in local dev...")
else:
    run_migrations_online()
