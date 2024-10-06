from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify
from database import User
from extensions import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# TODO: test function
def authenticate(username_or_email, password):
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    if user and user.verify_password(password):
        return user


@jwt.user_identity_loader
def user_identity_lookup(user: User):
    """
    Callback function uses when creating access tokens with `jwt.create_access_token`

    :param user:
        The identity (SQLAlchemy User object) that is passed into create_access_token.

    :return:
        The id of the user object
    """
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


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

    user = authenticate(username, password)

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)
