from sqlalchemy import String, ForeignKey, Enum, Numeric
from sqlalchemy.orm import mapped_column, Mapped, relationship
from decimal import Decimal
from uuid import UUID
from enum import Enum as PyEnum
from app.models import PerfiModel, PerfiSchema
from app.models.mixins import (
    UuidMixin,
    TimestampMixin,
    UuidMixinSchema,
    TimestampMixinSchema,
)


class AccountType(PyEnum):
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    CREDIT = "credit"
    CASH = "cash"


class Account(PerfiModel, UuidMixin, TimestampMixin):
    __tablename__ = "account"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.uuid", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, validate_strings=True), nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False, default=Decimal("0.00")
    )
    institution: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete"
    )

    def __repr__(self):
        return (
            f"<Account {self.name} ({self.account_type.value}) balance={self.balance}>"
        )


class AccountBaseSchema(PerfiSchema):
    name: str
    account_type: AccountType
    balance: Decimal = Decimal("0.00")
    institution: str | None = None
    description: str | None = None
    is_active: bool = True


class AccountSchema(AccountBaseSchema, UuidMixinSchema, TimestampMixinSchema):
    user_id: UUID


class AccountCreateSchema(AccountBaseSchema):
    user_id: UUID


class AccountUpdateSchema(PerfiSchema):
    name: str | None = None
    account_type: AccountType | None = None
    balance: Decimal | None = None
    institution: str | None = None
    description: str | None = None
    is_active: bool | None = None
