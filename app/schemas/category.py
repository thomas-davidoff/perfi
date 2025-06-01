from uuid import UUID as UuidType
from app.models import CategoryType
from pydantic import model_validator
from typing_extensions import Self
import warnings
from app.schemas import PerfiSchema, UuidMixinSchema, TimestampMixinSchema


class CategoryBaseSchema(PerfiSchema):
    name: str
    category_type: CategoryType
    is_system: bool = False
    user_id: UuidType | None = None

    @model_validator(mode="after")
    def check_user_id_and_system(self) -> Self:
        if self.is_system is True and self.user_id is not None:
            warnings.warn("User categories cannot be system categories.")
            self.is_system = False
        if self.user_id is None and self.is_system is False:
            raise ValueError(
                "is_system must be explictly set to True if user_id is not passed."
            )
        return self


class CategorySchema(CategoryBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    pass


class CategoryCreateSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(PerfiSchema):
    name: str | None = None
    category_type: CategoryType | None = None
