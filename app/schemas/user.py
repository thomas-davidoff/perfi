from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema
from pydantic import EmailStr, model_serializer, Field


class UserBaseSchema(PerfiSchema):
    email: EmailStr
    is_active: bool = True


class UserSchema(UserBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    hashed_password: bytes

    @model_serializer(when_used="json")
    def ser_model(self):
        return {k: v for k, v in self.model_dump().items() if k != "hashed_password"}


class UserCreateSchema(PerfiSchema):
    email: EmailStr
    password: str


class UserUpdateSchema(PerfiSchema):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
