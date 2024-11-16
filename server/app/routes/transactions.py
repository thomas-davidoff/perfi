from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from app.services import create_transactions_service

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@transactions_bp.route("/", methods=["GET"])
@jwt_required()
def get_transactions():
    transactions_service = create_transactions_service()
    transactions = transactions_service.get_transactions_for_user(
        user_id=current_user.id
    )
    serialized_transactions = [t.to_dict() for t in transactions]
    return jsonify(serialized_transactions), 200


@transactions_bp.route("/", methods=["POST"])
def create_transaction():
    pass
