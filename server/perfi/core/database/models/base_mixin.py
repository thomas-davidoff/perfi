from sqlalchemy import func, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
import uuid


class BaseMixin:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    _created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    _updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @property
    def created_at(self):
        """Allow reading the created_at value."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Disallow setting created_at after initial creation."""
        raise AttributeError("created_at is read-only.")

    @property
    def updated_at(self):
        """Allow reading the updated_at value."""
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        """Disallow manually setting updated_at."""
        raise AttributeError("updated_at is managed automatically.")
