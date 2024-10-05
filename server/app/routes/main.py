from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"msg": "all good"}), 200


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@main_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
