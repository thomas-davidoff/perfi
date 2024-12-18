from extensions import db
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TimestampMixin(object):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    _created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )

    _updated_at = db.Column(
        db.DateTime(timezone=True),
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

    def to_dict(self):
        """Convert to dictionary including updated_at."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
