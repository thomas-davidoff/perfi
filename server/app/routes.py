from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"msg": "all good"}), 200
