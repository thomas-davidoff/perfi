import os
from pathlib import Path
from fastapi import UploadFile
import csv
from io import TextIOWrapper, BytesIO
import shutil


class LocalFileService:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder

    async def save_file(self, file: UploadFile, user_id: str, file_name: str) -> str:
        """
        Save the file to the local file system under a user-specific directory.
        """
        user_folder = Path(self.upload_folder) / str(user_id)
        user_folder.mkdir(parents=True, exist_ok=True)

        file_path = user_folder / file_name

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return str(file_path)

    def delete_file(self, file_path: str) -> None:
        """
        Deletes a file from the local filesystem.
        """
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_file_path(self, user_id: str, filename: str) -> str:
        """
        Retrieves the file path based on user_id and filename.
        """
        return str(Path(self.upload_folder) / str(user_id) / filename)

    async def is_csv(self, file: UploadFile | None) -> bool:
        """
        Validates that the uploaded file is a valid CSV.
        """
        if file is None or not file.filename.lower().endswith(".csv"):
            return False

        try:
            raw_data = await file.read()
            file.file.seek(0)

            with TextIOWrapper(
                BytesIO(raw_data), encoding="utf-8", newline=""
            ) as text_stream:
                sample = text_stream.read(1024)
                text_stream.seek(0)

                sniffer = csv.Sniffer()
                sniffer.sniff(sample)

                text_stream.seek(0)
                reader = csv.reader(text_stream)
                for _ in range(10):
                    next(reader, None)

            file.file.seek(0)
        except (csv.Error, UnicodeDecodeError, ValueError):
            return False

        return True
