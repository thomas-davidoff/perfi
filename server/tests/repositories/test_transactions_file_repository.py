from uuid import UUID
from app.repositories import TransactionsFileImportRepository
from flask import Flask


def test_create_file_import(app: Flask, valid_user):

    repo = TransactionsFileImportRepository()
    data = {
        "filename": "test.csv",
        "file_path": "/tmp/uploads/12345/test.csv",
        "user_id": valid_user.id,
        "status": "pending",
    }
    file_import = repo.create(data)

    assert file_import.filename == "test.csv"
    assert file_import.status == "pending"
