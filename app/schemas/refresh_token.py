from datetime import datetime
from uuid import UUID
from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema


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
