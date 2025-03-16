from sqlalchemy import String, Enum, Boolean, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID as UuidType
from app.models import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)
from pydantic import model_validator
from typing_extensions import Self
import warnings


class CategoryType(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Category(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, validate_strings=True), nullable=False
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    transactions = relationship("Transaction", back_populates="category")

    user_id: Mapped[Optional[UuidType]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.uuid", ondelete="CASCADE"), nullable=True
    )
    user = relationship("User", back_populates="categories")

    def __repr__(self):
        return f"<Category name={self.name} type={self.category_type.value}>"


class CategoryBaseSchema(PerfiSchema):
    name: str
    category_type: CategoryType
    is_system: bool = False
    user_id: Optional[UuidType] = None

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
    name: Optional[str] = None
    category_type: Optional[CategoryType] = None
