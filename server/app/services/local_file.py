import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
import csv
from io import TextIOWrapper, BytesIO
import shutil


class LocalFileService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def save_file(self, file: FileStorage, user_id: str, file_name: str) -> str:
        """
        Save the file to the local file system under a user-specific directory.

        :param file: The file object to save.
        :param user_id: The ID of the user uploading the file.
        :return: The file path where the file is stored.
        """

        user_folder = Path(self.upload_folder) / str(user_id)
        user_folder.mkdir(parents=True, exist_ok=True)

        file_path = user_folder / file_name

        print(f"saving to {file_path}")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.stream, f)
        return str(file_path)

    def delete_file(self, file_path: str) -> None:
        """
        Deletes a file from the local filesystem.

        :param file_path: Path to the file to be deleted.
        """
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_file_path(self, user_id: str, filename: str) -> str:
        """
        Retrieves the file path based on user_id and filename.

        :param user_id: The ID of the user who uploaded the file.
        :param filename: The filename to retrieve.
        :return: The file path.
        """
        return str(Path(self.upload_folder) / str(user_id) / filename)

    def is_csv(self, file: FileStorage | None) -> bool:
        """
        Validates that the uploaded file is a valid CSV.

        :param file: FileStorage object representing the uploaded file.
        :return: True if the file is valid CSV, False otherwise.
        """
        if file is None:
            return False

        if not file.filename.lower().endswith(".csv"):
            return False

        try:
            file.stream.seek(0)
            raw_data = file.stream.read()

            with TextIOWrapper(
                BytesIO(raw_data), encoding="utf-8", newline=""
            ) as text_stream:
                sample = text_stream.read(1024)
                text_stream.seek(0)

                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                text_stream.seek(0)

                reader = csv.reader(text_stream, dialect=dialect)
                for _ in range(10):
                    next(reader, None)

            file.stream.seek(0)

        except (csv.Error, UnicodeDecodeError, ValueError) as e:
            print(f"CSV Validation Error: {e}")
            return False

        return True
