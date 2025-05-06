from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from uuid import UUID
from app.models import PerfiModel
from app.models.mixins import UuidMixin, TimestampMixin


class RefreshToken(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )
    token_value: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id}>"
