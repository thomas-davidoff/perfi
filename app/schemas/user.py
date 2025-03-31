from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema
from pydantic import EmailStr


class UserBaseSchema(PerfiSchema):
    email: EmailStr
    is_active: bool = True


class UserSchema(UserBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    hashed_password: bytes


class UserCreateSchema(PerfiSchema):
    email: EmailStr
    password: str


class UserUpdateSchema(PerfiSchema):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
