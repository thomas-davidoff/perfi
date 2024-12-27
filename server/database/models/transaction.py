from extensions import db
from sqlalchemy import Float, String, DateTime, Enum, func
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class TransactionCategory(enum.Enum):
    GROCERIES = "GROCERIES"
    UTILITIES = "UTILITIES"
    ENTERTAINMENT = "ENTERTAINMENT"
    TRANSPORTATION = "TRANSPORTATION"
    INCOME = "INCOME"
    OTHER = "OTHER"
    HOUSING = "HOUSING"
    UNCATEGORIZED = "UNCATEGORIZED"


class Transaction(TimestampMixin, db.Model):

    __tablename__ = "transactions"

    amount = db.Column(Float, nullable=False)
    description = db.Column(String(255), nullable=True)
    merchant = db.Column(String(255), nullable=False)
    date = db.Column(DateTime, default=func.now(), nullable=False)
    _category = db.Column(
        Enum(TransactionCategory, validate_strings=True),
        nullable=True,
        default=TransactionCategory.UNCATEGORIZED,
    )

    # Relationships
    file = db.relationship("TransactionsFile", back_populates="transactions")
    account = db.relationship("Account", back_populates="transactions")
    account_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("accounts.id"), nullable=False
    )

    file_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("transactions_files.id"), nullable=True
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
