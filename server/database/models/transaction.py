from extensions import db
from sqlalchemy import Float, String, DateTime, Enum, func
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID
import uuid


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

    # id = db.Column(db.Integer, primary_key=True)
    # TODO: account relationship
    # TODO: category relationship
    # TODO: source - manual, csv_import, etc

    amount = db.Column(Float, nullable=False)
    description = db.Column(String(255), nullable=True)
    merchant = db.Column(String(255), nullable=False)
    date = db.Column(DateTime, default=func.now(), nullable=False)
    category = db.Column(
        Enum(TransactionCategory, validate_strings=True),
        nullable=True,
        default=TransactionCategory.UNCATEGORIZED,
    )

    # relationships
    account = db.relationship("Account", back_populates="transactions")

    account_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("accounts.id"), nullable=False
    )
