from sqlalchemy import String, Enum, Boolean, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum as PyEnum
from typing import Optional
from db.base import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)


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

    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.uuid", ondelete="CASCADE"), nullable=True
    )
    user = relationship("User", back_populates="categories")

    def __repr__(self):
        return f"<Category {self.name} ({self.category_type.value})>"
