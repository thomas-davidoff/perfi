from sqlalchemy import Text, Column, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .mixins import RecordMixin
from .base import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        self._password_hash = pwd_context.hash(plain_text_password)

    def verify_password(self, password):
        """
        Verifies a password against its hashed version.
        """
        return pwd_context.verify(password, self._password_hash)

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
