from sqlalchemy import Text, Column, String
from sqlalchemy.orm import relationship
from .mixins import RecordMixin
from .base import Base
from perfi.core.utils import hash_password, verify_password


class User(Base, RecordMixin):
    __tablename__ = "users"

    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    _password_hash = Column("password", Text, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text_password):
        """
        Hashes a plain password.
        """
        self._password_hash = hash_password(plain_text_password)

    def verify_password(self, password):
        """
        Verifies a password against its hashed version.
        """
        return verify_password(password, self._password_hash)

    # relationships
    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    transactions_files = relationship(
        "TransactionsFile",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
