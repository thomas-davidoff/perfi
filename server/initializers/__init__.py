from .database import db
from .migrate import migrate
from .app_logger import create_logger


app_logger = create_logger("APP_LOGGER")


def init_app(app):
    app_logger.debug("Initializing application.")
    db.init_app(app)
    migrate.init_app(app, db)
