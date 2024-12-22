from extensions import db
from sqlalchemy import String, Enum, JSON
from .timestamp_mixin import TimestampMixin
import enum
from sqlalchemy.dialects.postgresql import UUID


class TransactionsFileImportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionsFileImport(TimestampMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint("filename", "user_id", name="uq_filename_user"),
    )

    filename = db.Column(String(255), nullable=False)
    file_path = db.Column(String(1024), nullable=True)
    error_log = db.Column(JSON, nullable=True)
    user = db.relationship("User", back_populates="file_imports")
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    status = db.Column(
        Enum(TransactionsFileImportStatus, validate_strings=True),
        nullable=False,
        default=TransactionsFileImportStatus.PENDING,
    )
    processed_at = db.Column(db.DateTime, nullable=True)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
