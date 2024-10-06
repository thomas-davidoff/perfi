from flask import Flask
from initializers import init_app
from config import logger, configuration


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

        # from cli import CLI_GROUPS
        from app.cli import CLI_GROUPS

        for g in CLI_GROUPS:
            app.cli.add_command(g)

    return app
