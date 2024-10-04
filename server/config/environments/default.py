import os
from urllib.parse import quote_plus as url_quote_plus


class Config:
    def __init__(self) -> None:
        # misc secrets
        self.SECRET_KEY = os.environ["SECRET_KEY"]

        # Will use sqlalchemy's event system instead of flask-sqlalchemy
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # Database configuration
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        # safely encode the password to avoid misinterpretation
        db_pass = url_quote_plus(os.environ["DB_PASS"])

        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )
