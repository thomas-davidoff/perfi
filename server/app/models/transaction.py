from sqlalchemy import Float, String, DateTime, Enum, func, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base_mixin import BaseMixin
from .base import Base
import enum


class TransactionCategory(enum.Enum):
    GROCERIES = "GROCERIES"
    UTILITIES = "UTILITIES"
    ENTERTAINMENT = "ENTERTAINMENT"
    TRANSPORTATION = "TRANSPORTATION"
    INCOME = "INCOME"
    OTHER = "OTHER"
    HOUSING = "HOUSING"
    UNCATEGORIZED = "UNCATEGORIZED"


class Transaction(Base, BaseMixin):

    __tablename__ = "transactions"

    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    merchant = Column(String(255), nullable=False)
    date = Column(DateTime, default=func.now(), nullable=False)
    _category = Column(
        Enum(TransactionCategory, validate_strings=True),
        nullable=True,
        default=TransactionCategory.UNCATEGORIZED,
    )

    # Relationships
    file = relationship("TransactionsFile", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    file_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions_files.id"), nullable=True
    )

    @property
    def category(self):
        if self._category is None:
            return None
        return self._category.value

    @category.setter
    def category(self, value):
        if isinstance(value, str):
            value = value.upper()
            self._category = TransactionCategory(value)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "amount": self.amount,
                "description": self.description,
                "merchant": self.merchant,
                "date": self.date.strftime("%m-%d-%Y"),
                "category": self.category,
                "account": self.account.compact(),
            }
        )
        return base_dict
