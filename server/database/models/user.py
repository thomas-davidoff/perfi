from extensions import db, bcrypt
from sqlalchemy import Text
from .timestamp_mixin import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

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

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

    # relationships
    accounts = db.relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
