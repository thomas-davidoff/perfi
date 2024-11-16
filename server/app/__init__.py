from initializers import init_extensions, get_logger
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from extensions import db
import os
from .exceptions import CustomException
import traceback

logger = get_logger("APP_LOGGER", os.getenv("LOG_LEVEL"))


def error_respond(message, status=200, **kwargs):
    """
    Helper function to create a JSON response with a consistent format.
    """
    response_data = {"error": message}
    response_data.update(kwargs)
    return jsonify(response_data), status


def create_app(config, init_logger=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.logger = logger

    init_extensions(app, init_logger)

    with app.app_context():
        from app.routes import main_bp, auth_bp, transactions_bp, accounts_bp

        blueprints = [main_bp, auth_bp, transactions_bp, accounts_bp]

        for bp in blueprints:
            app.register_blueprint(bp)

        from app.cli import CLI_GROUPS

        for group in CLI_GROUPS:
            app.cli.add_command(group)

        @app.before_request
        def log_request():
            remote_ip = request.environ.get("REMOTE_ADDR")
            remote_port = request.environ.get("REMOTE_PORT")
            url = request.url
            method = request.method
            user_agent = request.user_agent
            logger.info(
                f"{method} request from {remote_ip}:{remote_port} to {url}; user-agent: {user_agent}"
            )

        @app.after_request
        def remove_session(response):
            db.session.remove()
            return response

        @app.errorhandler(Exception)
        def handle_exception(e):
            logger.error(f"{type(e)}: {e}")
            logger.error(traceback.format_exc())
            if isinstance(e, CustomException):
                return error_respond(e.msg, e.code)
            elif isinstance(e, HTTPException):
                return error_respond(str(e), e.code)
            else:
                return error_respond(f"Internal server error: {str(e)}", 500)

    return app
