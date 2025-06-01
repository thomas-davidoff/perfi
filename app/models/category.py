from sqlalchemy import String, Enum, Boolean, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum as PyEnum
from uuid import UUID as UuidType
from app.models import PerfiModel
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
)


class CategoryType(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Category(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, validate_strings=True), nullable=False
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    transactions = relationship("Transaction", back_populates="category")

    user_id: Mapped[UuidType | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=True
    )
    user = relationship("User", back_populates="categories")

    def __repr__(self):
        return f"<Category name={self.name} type={self.category_type.value}>"
