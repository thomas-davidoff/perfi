from sqlalchemy import String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timedelta
from uuid import UUID
from .base_model import BaseModel
from typing import Optional


class RefreshToken(BaseModel):
    __tablename__ = "refresh_token"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    token_value: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now() + timedelta(days=7)
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id} expires_at={self.expires_at}>"
