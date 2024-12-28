from initializers import init_extensions
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from extensions import db
from .exceptions import CustomException
import traceback

import logging

logger = logging.getLogger(__name__)


def error_respond(message: str, status=200, **kwargs):
    """
    Helper function to create a JSON response with a consistent format.
    """

    if not isinstance(message, str):
        logger.error(
            f"Message must be str to respond with error_respond. {str(type(message))} was passed instead."
        )
        return jsonify({"error": "Unknown error"}), 500

    response_data = {"error": message}
    response_data.update(kwargs)
    return jsonify(response_data), status


def create_app(config):
    logger.info(f"Creating app using {config.name} configuration")
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config)

    init_extensions(app)

    with app.app_context():
        from app.routes import (
            main_bp,
            auth_bp,
            transactions_bp,
            accounts_bp,
            file_import_bp,
        )

        blueprints = [main_bp, auth_bp, transactions_bp, accounts_bp, file_import_bp]

        for bp in blueprints:
            local_prefix = bp.url_prefix or ""
            prefix = "/api" + local_prefix
            app.register_blueprint(bp, url_prefix=prefix)

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
            logger.error(f"{type(e)}: {e}" + "\n" + traceback.format_exc())
            if isinstance(e, CustomException):
                return error_respond(e.msg, e.code)
            elif isinstance(e, HTTPException):
                return error_respond(str(e), e.code)
            else:
                return error_respond(
                    f"An unexpected error occured. Contact the application owner.", 500
                )

    return app
