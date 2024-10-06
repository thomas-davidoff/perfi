from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, current_user, jwt_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"msg": "all good"}), 200


@main_bp.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    return jsonify(current_user.dump())
