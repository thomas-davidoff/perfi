from .database import db
from .migrate import migrate


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
