from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify, g
from app.services import AuthService
from typing import cast
from app.repositories import UserRepository
from app import logger

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# set up auth routes
@auth_bp.before_request
def init_services():
    g.user_repository = UserRepository()
    g.auth_service = AuthService(g.user_repository)


def get_user_service() -> AuthService:
    return cast(AuthService, g.auth_service)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login route for authentication.

    Expects a POST request to this path, including a valid username and password in the json payload.

    :return:
        An access token used to authorize user access to protected routes.
    """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    auth_service = get_user_service()

    user = auth_service.authenticate(username, password)

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)
