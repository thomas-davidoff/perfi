from extensions import db
from sqlalchemy import Float, String, DateTime, Enum, func
from .timestamp_mixin import TimestampMixin
import enum


class TransactionCategory(enum.Enum):
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    INCOME = "income"
    OTHER = "other"
    HOUSING = "housing"


class Transaction(TimestampMixin, db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    # TODO: account relationship
    # TODO: category relationship
    # TODO: source - manual, csv_import, etc

    amount = db.Column(Float, nullable=False)
    description = db.Column(String(255), nullable=True)
    merchant = db.Column(String(255), nullable=False)
    date = db.Column(DateTime, default=func.now(), nullable=False)
    category = db.Column(
        Enum(TransactionCategory), nullable=True, default=TransactionCategory.OTHER
    )