from flask import Blueprint, request, jsonify, current_app
from app.services import create_file_import_service
from app.exceptions import ApiError
from flask_jwt_extended import jwt_required, current_user

file_import_bp = Blueprint("file_import", __name__, url_prefix="/files")
file_service = create_file_import_service(current_app.config.get("UPLOAD_FOLDER"))


@file_import_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():

    user_id = current_user.id

    file = request.files.get("transactions")
    account_id = request.form.get("account_id")

    if not file or not account_id:
        raise ApiError(msg="File and account ID are required.", code=422)

    file_record, headers = file_service.save_and_preview(
        file=file, user_id=user_id, account_id=account_id
    )
    return jsonify(
        {
            "file_id": str(file_record.id),
            "headers": headers,
            "preview": file_record.preview_data,
        }
    )


@file_import_bp.route("/", methods=["GET"])
@jwt_required()
def list_files():
    transaction_files_service = create_file_import_service(
        current_app.config.get("UPLOAD_FOLDER")
    )

    return jsonify(transaction_files_service.list_files_for_user(current_user.id)), 200


@file_import_bp.route("/<file_id>", methods=["GET"])
@jwt_required()
def get_file(file_id):
    transaction_files_service = create_file_import_service(
        current_app.config.get("UPLOAD_FOLDER")
    )

    return jsonify(
        transaction_files_service.get_file_metadata(
            file_id=file_id, user_id=current_user.id
        )
    )


@file_import_bp.route("/map-headers/<file_id>", methods=["POST"])
@jwt_required()
def map_headers(file_id):
    transaction_files_service = create_file_import_service(
        current_app.config.get("UPLOAD_FOLDER")
    )

    mapped_headers = request.json.get("mapped_headers")
    if not mapped_headers:
        raise ApiError("Mapped headers are reqired")

    print(mapped_headers)

    transaction_files_service.map_headers(
        file_id=file_id, mapped_headers=mapped_headers
    )
    return mapped_headers


# @file_import_bp.route("/map-headers/<file_id>", methods=["POST"])
# def map_headers(file_id):
#     mapped_headers = request.json.get("mapped_headers")
#     if not mapped_headers:
#         return jsonify({"error": "Mapped headers are required"}), 400

#     file_service.map_headers(file_id, mapped_headers)
#     return jsonify({"message": "Headers mapped successfully"})


# @file_import_bp.route("/import/<file_id>", methods=["POST"])
# def import_file(file_id):
#     file_service.import_file(file_id)
#     return jsonify({"message": "File imported successfully"})
