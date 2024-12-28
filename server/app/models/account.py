from sqlalchemy import Float, String, Enum, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base_mixin import BaseMixin
from .base import Base
import enum


class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"


class Account(Base, BaseMixin):
    __tablename__ = "accounts"

    name = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    account_type = Column(Enum(AccountType, validate_strings=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # relationships
    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    user = relationship("User", back_populates="accounts")

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "name": self.name,
                "balance": self.balance,
                "account_type": self.account_type.value,
                "user_id": self.user.to_dict(),
            }
        )
        return base_dict

    def compact(self):
        return {
            "name": self.name,
            "id": self.id,
            "account_type": self.account_type.value,
        }
