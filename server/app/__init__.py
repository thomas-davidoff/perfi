from flask import Flask, g
from initializers import init_app
from config import logger, configuration
from app.repositories import UserRepository
from app.services import AuthService
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(configuration)
    app.logger = logger

    # Initialize extensions
    init_app(app)

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
