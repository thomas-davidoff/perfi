from sqlalchemy import DateTime, func, UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .mixins import IDMixin
from .base import Base


class RefreshToken(Base, IDMixin):
    """
    Refresh token model
    """

    __tablename__ = "refresh_tokens"

    issued_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    token: Mapped[String] = mapped_column(String, nullable=False, unique=True)

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user = relationship("User", back_populates="refresh_tokens")
