from extensions import db, bcrypt, migrate, jwt
import os
import logging

logger = logging.getLogger(__name__)


def init_extensions(app):
    logger.info("Initializing extensions")
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
