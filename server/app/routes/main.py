from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, current_user, jwt_required
from database import User
from typing import cast

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"msg": "all good"}), 200


@main_bp.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    cur_user = cast(User, current_user)
    return jsonify(cur_user.to_dict())
