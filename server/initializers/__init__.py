from .migrate import migrate
from database import db
from config import logger


def init_app(app):
    logger.debug("Initializing application")
    db.init_app(app)
    migrate.init_app(app, db)
