from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import Enum as PyEnum
from .base_model import BaseModel
from typing import Optional


class CategoryType(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Category(BaseModel):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, validate_strings=True), nullable=False
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(7), nullable=False, default="#000000"
    )  # Hex color code
    icon: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Relationships
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name} ({self.category_type.value})>"
