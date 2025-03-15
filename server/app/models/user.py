from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped, relationship
import bcrypt

from app.models import PerfiModel, PerfiSchema
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

    def __repr__(self):
        return f"<User username={self.username} email={self.email} active={self.is_active}>"


class UserBaseSchema(PerfiSchema):
    username: str
    email: str
    is_active: bool = True


class UserSchema(UserBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    hashed_password: bytes


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(PerfiSchema):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: str | None = None
