from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import URL
from app.core.database import Base
import logging
from config import DATABASE_URL_SYNC


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
