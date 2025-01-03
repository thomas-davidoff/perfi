from sqlalchemy.engine.url import URL
from perfi.core.dependencies.settings import get_settings


settings = get_settings()


def get_database_urls():
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
    return DATABASE_URL_ASYNC, DATABASE_URL_SYNC


from alembic.script import ScriptDirectory
from alembic.config import Config
from sqlalchemy import engine_from_config, pool, Engine


def configure_alembic():
    """
    Configure Alembic with the database connection and script location.
    Returns:
        alembic_cfg: The Alembic Config object
        script: The Alembic ScriptDirectory
        engine: The SQLAlchemy engine
    """

    _, DATABASE_URL_SYNC = get_database_urls()

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(DATABASE_URL_SYNC))

    script = ScriptDirectory.from_config(alembic_cfg)

    engine: Engine = engine_from_config(
        {"sqlalchemy.url": str(DATABASE_URL_SYNC)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    return alembic_cfg, script, engine
