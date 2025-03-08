from sqlalchemy import Float, String, Enum, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from perfi.schemas.account import AccountType
from .mixins import RecordMixin
from .base import Base


class Account(Base, RecordMixin):
    __tablename__ = "accounts"

    name = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_type = Column(
        Enum(AccountType, validate_strings=True),
        nullable=False,
    )

    # relationships
    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    user = relationship("User", back_populates="accounts", lazy="selectin")

    def compact(self):
        return {
            "name": self.name,
            "id": self.id,
            "account_type": self.account_type.value,
        }
