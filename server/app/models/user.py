from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped, relationship
import bcrypt

from db.base import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)


class User(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hashed_password: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="TRUE")

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete"
    )
    accounts = relationship("Account", back_populates="user", cascade="all, delete")
    categories = relationship("Category", back_populates="user", cascade="all, delete")

    # @property
    # def password(self):
    #     raise AttributeError("Password is write-only.")

    # @password.setter
    # def password(self, password):
    #     """
    #     Hashes a plain password.
    #     """
    #     pwd_bytes = password.encode("utf-8")
    #     salt = bcrypt.gensalt()
    #     hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    #     self._password_hash = hashed_password

    # def verify_password(self, password):
    #     """
    #     Verifies a password against its hashed version.
    #     """
    #     return bcrypt.checkpw(
    #         password=password.encode("utf-8"),
    #         hashed_password=self._password_hash,
    #     )

    def __repr__(self):
        return f"<User {self.username}>"


class UserBaseSchema(PerfiSchema):
    username: str
    email: str
    is_active: bool = True


class UserSchema(UserBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    hashed_password: str


class UserInSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(PerfiSchema):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: str | None = None
