from uuid import UUID
from app.repositories import TransactionsFileRepository
from flask import Flask


def test_create_file_import(app: Flask, valid_account):

    repo = TransactionsFileRepository()
    data = {
        "filename": "test.csv",
        "file_path": "/tmp/uploads/12345/test.csv",
        "user_id": valid_account.user_id,
        "status": "pending",
        "account_id": valid_account.id,
    }
    file_import = repo.create(data)

    assert file_import.filename == data["filename"]
    assert file_import.status == data["status"]
