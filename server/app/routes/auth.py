from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify, g
from app.services import AuthService, create_auth_service
from typing import cast
from app.exceptions import (
    MissingPayload,
    MissingLoginData,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# set up auth routes
@auth_bp.before_request
def init_services():
    g.auth_service = create_auth_service()


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
    data = request.get_json(silent=True)
    if not data:
        raise MissingPayload

    # Extract fields from the JSON body if it's valid
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise MissingLoginData

    auth_service = get_user_service()

    user = auth_service.authenticate(username, password)

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registration route.
    """

    auth_service = get_user_service()

    user_data = request.get_json(silent=True)

    if not user_data:
        raise MissingPayload

    user = auth_service.register_user(
        username=user_data.get("username"),
        password=user_data.get("password"),
        email=user_data.get("email"),
    )

    return jsonify(user.to_dict()), 201
