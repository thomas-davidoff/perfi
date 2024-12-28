from sqlalchemy import Float, String, DateTime, Enum, func, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base_mixin import BaseMixin
from perfi.core.database import Base
from perfi.schemas.transaction import TransactionCategory


class Transaction(Base, BaseMixin):

    __tablename__ = "transactions"

    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    merchant = Column(String(255), nullable=False)
    date = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    _category = Column(
        Enum(TransactionCategory, validate_strings=True),
        nullable=True,
        default=TransactionCategory.UNCATEGORIZED,
    )

    # Relationships
    file = relationship(
        "TransactionsFile", back_populates="transactions", lazy="selectin"
    )
    account = relationship("Account", back_populates="transactions", lazy="selectin")
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

    @property
    def user_id(self):
        """
        This allows a 'belongs to' check, as transactions are two hops away from a user
        """
        return self.account.user_id
