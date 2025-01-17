from sqlalchemy import String, Enum, JSON, ForeignKey, Column, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
from perfi.schemas import TransactionsFileImportStatus
from .mixins import RecordMixin
from .base import Base


class TransactionsFile(Base, RecordMixin):
    __tablename__ = "transactions_files"
    __table_args__ = (UniqueConstraint("filename", "user_id", name="uq_filename_user"),)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    _status = Column(
        Enum(TransactionsFileImportStatus, validate_strings=True),
        nullable=False,
        default=TransactionsFileImportStatus.PENDING,
    )
    preview_data = Column(JSON, nullable=True)
    mapped_headers = Column(JSON, nullable=True)
    error_log = Column(JSON, nullable=True)

    account_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="transactions_files", lazy="selectin")
    transactions = relationship("Transaction", back_populates="file", lazy="selectin")

    @property
    def status(self):
        return self._status.value

    @status.setter
    def status(self, value):
        if isinstance(value, str):
            value = value.upper()
        self._status = TransactionsFileImportStatus(value)
