from extensions import db
from sqlalchemy import Float, String, DateTime, Enum, func
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID


class TransactionCategory(enum.Enum):
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    INCOME = "income"
    OTHER = "other"
    HOUSING = "housing"
    UNCATEGORIZED = "uncategorized"


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

    # many-to-one with accounts
    account = db.relationship("Account", back_populates="transactions")
    account_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("accounts.id"), nullable=False
    )

    @property
    def category(self):
        return self._category.value

    @category.setter
    def category(self, value):
        if isinstance(value, str):
            value = value.lower()
        self._category = TransactionCategory(value)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "amount": self.amount,
                "description": self.description,
                "merchant": self.merchant,
                "date": self.date.strftime("%m-%d-%Y"),
                "category": self.category.value,
                "account": self.account.compact(),
            }
        )
        return base_dict
