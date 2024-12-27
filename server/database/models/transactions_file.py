from extensions import db
from sqlalchemy import String, Enum, JSON
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped


class TransactionsFileImportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATED = "validated"
    IMPORTED = "imported"
    FAILED = "failed"

    # TODO: Remove below normalization
    # def __new__(cls, value):
    #     if isinstance(value, str):
    #         value = value.upper()
    #     obj = object.__new__(cls)
    #     obj._value_ = value
    #     return obj


class TransactionsFile(TimestampMixin, db.Model):
    __tablename__ = "transactions_files"
    __table_args__ = (
        db.UniqueConstraint("filename", "user_id", name="uq_filename_user"),
    )
    filename = db.Column(String(255), nullable=False)
    file_path = db.Column(String(1024), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    _status = db.Column(
        Enum(TransactionsFileImportStatus, validate_strings=True),
        nullable=False,
        default=TransactionsFileImportStatus.PENDING,
    )
    preview_data = db.Column(JSON, nullable=True)
    mapped_headers = db.Column(JSON, nullable=True)
    error_log = db.Column(JSON, nullable=True)
    user = db.relationship("User", back_populates="transactions_files")

    account_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("accounts.id"), nullable=False
    )

    @property
    def status(self):
        return self._status.value

    @status.setter
    def status(self, value):
        if isinstance(value, str):
            value = value.lower()
        # normalize to lowercase, but ensure that enum members are also lowered.
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
