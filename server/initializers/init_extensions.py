from extensions import db, bcrypt, migrate, jwt


def init_extensions(app, logger):
    logger.debug("initializing extensions...")

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
