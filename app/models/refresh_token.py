from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from uuid import UUID
from app.models import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)


class RefreshToken(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "refresh_token"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.uuid", ondelete="CASCADE"), nullable=False
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


class RefreshTokenBaseSchema(PerfiSchema):
    user_id: UUID
    token_value: str
    expires_at: datetime
    last_used_at: datetime | None = None
    device_info: str | None = None
    revoked: bool = False
    revoked_at: datetime | None = None


class RefreshTokenSchema(RefreshTokenBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    pass


class RefreshTokenCreateSchema(RefreshTokenBaseSchema):
    pass


class RefreshTokenUpdateSchema(PerfiSchema):
    last_used_at: datetime | None = None
    revoked: bool | None = None
    revoked_at: datetime | None = None
