from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import PerfiModel
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
)


class User(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    hashed_password: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="TRUE")

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete"
    )
    accounts = relationship("Account", back_populates="user", cascade="all, delete")
    categories = relationship("Category", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User email={self.email} active={self.is_active}>"
