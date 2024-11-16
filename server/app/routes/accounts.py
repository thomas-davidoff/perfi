from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from app.services import create_user_service, create_accounts_service
from database import Account

accounts_bp = Blueprint("accounts", __name__, url_prefix="/accounts")


@accounts_bp.route("/", methods=["GET"])
@jwt_required()
def get_accounts():
    user_service = create_user_service()

    accounts = user_service.get_user_accounts(user_id=current_user.id)
    serialized_accounts = [a.to_dict() for a in accounts]
    return jsonify(serialized_accounts), 200


@accounts_bp.route("/", methods=["POST"])
@jwt_required()
def create_account():
    accounts_service = create_accounts_service()

    account = accounts_service.create_account(
        user_id=current_user.id, data=request.get_json()
    )
    return jsonify(account.to_dict()), 200
