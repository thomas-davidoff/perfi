import os
from urllib.parse import quote_plus as url_quote_plus
from datetime import timedelta
from pathlib import Path


class DefaultConfig:
    name = "default"

    def __init__(self, logger=None) -> None:
        if logger:
            logger.debug(f"Loading {self.name} config...")
        # misc secrets
        self.SECRET_KEY = os.environ["SECRET_KEY"]

        # Will use sqlalchemy's event system instead of flask-sqlalchemy
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # Database configuration
        db_host = os.environ.get("DB_HOST")
        db_port = os.environ.get("DB_PORT")
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_pass = os.environ.get("DB_PASS")

        # safely encode the password to avoid misinterpretation
        if db_pass:
            db_pass = url_quote_plus(db_pass)

        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )

        self.JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(
            seconds=int(os.environ["JWT_ACCESS_TOKEN_EXPIRES"])
        )

        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(
            seconds=int(os.environ["JWT_REFRESH_TOKEN_EXPIRES"])
        )

        uploads_folder = os.environ.get("UPLOAD_FOLDER", "uploads")
        uploads_folder_absolute = Path.absolute(
            Path.joinpath(Path.cwd(), Path(uploads_folder))
        )
        # create the uploads folder
        Path.mkdir(uploads_folder_absolute, mode=500, exist_ok=True)

        self.UPLOAD_FOLDER = uploads_folder_absolute
