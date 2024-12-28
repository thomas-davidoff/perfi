from initializers import init_extensions
from flask import Flask, jsonify, request, g
from werkzeug.exceptions import HTTPException
from extensions import db
from .exceptions import CustomException
import traceback
import time

import logging

logger = logging.getLogger(__name__)
request_logger = logging.getLogger("request_logger")


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
        def save_request_start():
            g.start_time = time.time()

        @app.after_request
        def log_request_end(response):
            duration = time.time() - g.start_time
            msg = f"Completed {request.method} @ {request.url} for {request.environ.get('REMOTE_ADDR')} with status {response.status_code} in {duration:.3f} seconds"

            if 200 <= response.status_code < 300:
                request_logger.info(msg)
            elif 300 <= response.status_code < 400:
                request_logger.warning(msg)
            elif 400 <= response.status_code < 400:
                request_logger.error(msg)
            else:
                request_logger.critical(msg)

            return response

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
