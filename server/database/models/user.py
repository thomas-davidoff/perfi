# database/models/user.py

from extensions import db, bcrypt
from config import logger
from sqlalchemy import Text, func, text
from initializers import bcrypt


class TimestampMixin(object):
    # NOW() AT TIME ZONE \'UTC\' is postgresql specific.
    # However, it ensures ts will be created in utc time without having to call python datetime
    # created_at = db.Column(
    #     db.DateTime(timezone=True), default=text("NOW() AT TIME ZONE 'UTC'")
    # )
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())


# Just a basic table for now to test things.
class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column("password", Text, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text_password):
        self._password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def dump(self):
        return {"id": self.id, "username": self.username, "email": self.email}
