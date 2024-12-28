from sqlalchemy import String, Enum, JSON, ForeignKey, Column, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
from .base_mixin import BaseMixin
from app.core.database import Base
import enum


class TransactionsFileImportStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VALIDATED = "VALIDATED"
    IMPORTED = "IMPORTED"
    FAILED = "FAILED"


class TransactionsFile(Base, BaseMixin):
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
    user = relationship("User", back_populates="transactions_files")
    transactions = relationship("Transaction", back_populates="file", lazy="dynamic")

    @property
    def status(self):
        return self._status.value

    @status.setter
    def status(self, value):
        if isinstance(value, str):
            value = value.upper()
        self._status = TransactionsFileImportStatus(value)

    def to_dict(self):
        base_dict = super().to_dict()

        base_dict.update(
            {
                "filename": self.filename,
                "file_path": self.file_path,
                "status": self.status,
                "mapped_headers": self.mapped_headers,
                "preview": self.preview_data,
                "errors": self.error_log,
            }
        )
        return base_dict

    def compact(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "filename": self.filename,
                "file_path": self.file_path,
                "status": self.status,
            }
        )
        return base_dict
