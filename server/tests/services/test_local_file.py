import pytest
from pathlib import Path
import csv
from werkzeug.datastructures import FileStorage
from perfi.services import LocalFileService
from flask import Flask
import tempfile


@pytest.fixture
def tmp_csv_fp():
    to_csv = [
        {"name": "bob", "age": 25},
        {"name": "jim", "age": 31},
    ]
    keys = to_csv[0].keys()

    with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="") as temp_file:
        dict_writer = csv.DictWriter(temp_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)

        temp_file.flush()
        temp_file.seek(0)

        yield temp_file.name


def test_save_file(app: Flask, tmp_csv_fp):
    upload_folder = app.config.get("UPLOAD_FOLDER")
    assert upload_folder is not None
    print(f"Upload folder: {upload_folder}")

    file_service = LocalFileService(upload_folder)

    with open(tmp_csv_fp, "rb") as file_stream:
        file = FileStorage(stream=file_stream, filename="test.csv")
        user_id = "12345"
        saved_path = file_service.save_file(file, user_id, file_name="test.csv")

    print(f"Saved file path: {saved_path}")
    assert Path(saved_path).exists()

    with open(saved_path, "r") as saved_file:
        content = saved_file.read()
        print(f"Saved file content: {content}")
        assert "bob" in content
        assert "jim" in content

    if Path(saved_path).exists():
        Path(saved_path).unlink()  # remove file
        Path(saved_path).parent.rmdir()  # removes user dir

    Path(upload_folder).rmdir()  # remove test upload dir
