# initializers/__init__.py

from config import logger
from extensions import db, bcrypt, migrate, jwt


def init_app(app):
    logger.debug("Initializing application")
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
