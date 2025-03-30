from sqlalchemy import ForeignKey, String, Boolean, Numeric, Text, Date
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import date as dt
from decimal import Decimal
from uuid import UUID
from app.models import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)


class Transaction(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "transaction"

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("account.uuid", ondelete="CASCADE"), nullable=False, index=True
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("category.uuid", ondelete="CASCADE"), nullable=False, index=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False, index=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.description} ${self.amount} on {self.date}>"


class TransactionBaseSchema(PerfiSchema):
    account_id: UUID
    amount: Decimal
    description: str
    date: dt
    is_pending: bool = False
    notes: str | None = None
    category_id: UUID = None


class TransactionSchema(TransactionBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    pass


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionUpdateSchema(PerfiSchema):
    amount: Decimal | None = None
    description: str | None = None
    date: dt | None = None
    is_pending: bool | None = None
    notes: str | None = None
    category_id: UUID | None = None
