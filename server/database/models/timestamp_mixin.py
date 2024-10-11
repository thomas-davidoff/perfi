from extensions import db
from sqlalchemy import func


class TimestampMixin(object):
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )

    @property
    def created_at(self):
        """Allow reading the created_at value."""
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        """Disallow setting created_at after initial creation."""
        raise AttributeError("created_at is read-only.")
