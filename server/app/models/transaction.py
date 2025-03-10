from sqlalchemy import ForeignKey, String, Boolean, Numeric, Text, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import date as dt
from decimal import Decimal
from uuid import UUID
from typing import Optional
from .base_model import BaseModel


class Transaction(BaseModel):
    __tablename__ = "transaction"

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # The category_id doesn't have a default in the model
    # Defaults are handled in the service layer
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"), nullable=False, index=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False, index=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
