from extensions import db
from sqlalchemy import Float, String, Enum
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID


class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"


class Account(TimestampMixin, db.Model):
    __tablename__ = "accounts"

    # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    balance = db.Column(Float, nullable=False, default=0.0)
    account_type = db.Column(Enum(AccountType, validate_strings=True), nullable=False)

    # relationships
    transactions = db.relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    user = db.relationship("User", back_populates="accounts")
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance,
            "account_type": self.account_type.value,
            "user_id": self.user.to_dict(),
        }
