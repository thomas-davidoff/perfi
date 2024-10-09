from initializers import init_extensions, get_logger
from flask import Flask
from extensions import db
import os

logger = get_logger("APP_LOGGER", os.getenv("LOG_LEVEL"))


def create_app(config, init_logger=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.logger = logger

    # Initialize extensions
    init_extensions(app, init_logger)

    # Register blueprints
    with app.app_context():
        from app.routes import main_bp, auth_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)

        from app.cli import CLI_GROUPS

        for group in CLI_GROUPS:
            app.cli.add_command(group)

        @app.after_request
        def remove_session(response):
            db.session.remove()
            return response

    return app
