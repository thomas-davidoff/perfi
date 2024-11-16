from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    decode_token,
)
from flask import Blueprint, request, jsonify, g
from app.services import AuthService, create_auth_service, create_user_service
from typing import cast
from app.exceptions import (
    MissingPayload,
    MissingLoginData,
)
from datetime import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.before_request
def init_services():
    g.auth_service = create_auth_service()


def get_user_service() -> AuthService:
    return cast(AuthService, g.auth_service)


def get_token_expiry(token):
    ts = decode_token(token)["exp"]
    return datetime.fromtimestamp(ts).isoformat()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login route for authentication.

    Expects a POST request to this path, including a valid username and password in the json payload.

    :return:
        Access and refresh tokens used for user authentication.
    """
    data = request.get_json(silent=True)
    if not data:
        raise MissingPayload

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise MissingLoginData

    auth_service = get_user_service()
    user = auth_service.authenticate(username, password)

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user, fresh=True)
    print("kajnsdkajsnd")
    refresh_token = create_refresh_token(identity=user)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires=get_token_expiry(access_token),
        refresh_token_expires=get_token_expiry(refresh_token),
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh route to get a new access token.
    """
    current_user = get_jwt_identity()
    user_service = create_user_service()
    user = user_service.get_by_id(current_user)
    if not user:
        raise Exception("Unexpected error. Contact application owner.")
    new_access_token = create_access_token(identity=user)

    return jsonify(
        access_token=new_access_token,
        access_token_expires=get_token_expiry(new_access_token),
    )


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
