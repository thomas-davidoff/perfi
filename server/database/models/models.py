from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from config import logger
from sqlalchemy import Text


# Just a basic table for now to test things.
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column("password", Text, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        logger.debug("password prop")
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text_password):
        logger.debug("password setter")
        self._password_hash = generate_password_hash(plain_text_password)

    def verify_password(self, password):
        logger.debug("verify password")
        return check_password_hash(self._password_hash, password)
