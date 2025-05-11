from app.schemas import UuidMixinSchema, TimestampMixinSchema


class ApiResourceCompact(UuidMixinSchema):
    pass


class ApiResourceFull(ApiResourceCompact, TimestampMixinSchema):
    pass
