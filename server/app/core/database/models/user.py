from sqlalchemy import Text, Column, String
from sqlalchemy.orm import relationship
from .base_mixin import BaseMixin
from passlib.context import CryptContext
from app.core.database import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base, BaseMixin):
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
        self._password_hash = pwd_context.hash(plain_text_password)

    def verify_password(self, password):
        return pwd_context.verify(password, self._password_hash)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {"id": self.id, "username": self.username, "email": self.email}
        )
        return base_dict

    # relationships
    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    transactions_files = relationship(
        "TransactionsFile",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
