from flask import Flask
from initializers import init_app
from config import logger, configuration
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config.from_object(configuration)
    app.logger = logger

    jwt = JWTManager(app)

    # Initialize extensions
    init_app(app)

    # Register blueprints
    with app.app_context():
        from app.routes import main_bp, auth_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)

        # from cli import CLI_GROUPS
        from app.cli import CLI_GROUPS

        for g in CLI_GROUPS:
            app.cli.add_command(g)

    return app
