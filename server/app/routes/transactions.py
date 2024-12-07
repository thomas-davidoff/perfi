from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from app.services import (
    create_transactions_service,
)
from app.exceptions import MissingPayload

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@transactions_bp.route("/", methods=["GET"])
@jwt_required()
def get_transactions():
    transactions_service = create_transactions_service()
    transactions = transactions_service.get_transactions_by_user_id(
        user_id=current_user.id
    )
    serialized_transactions = [t.to_dict() for t in transactions]
    return jsonify(serialized_transactions), 200


@transactions_bp.route("/", methods=["POST"])
@jwt_required()
def create_transaction():
    """
    Route that creates a transaction
    """

    transactions_service = create_transactions_service()
    transactions_data = request.get_json()

    if not transactions_data:
        raise MissingPayload
    transaction = transactions_service.create_transaction(request.get_json())

    return jsonify(transaction.to_dict()), 201


@transactions_bp.route("/<transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    transactions_service = create_transactions_service()
    transactions_service.delete_transaction(transaction_id)
    return jsonify({"msg": f"Transaction {transaction_id} deleted."}), 200
