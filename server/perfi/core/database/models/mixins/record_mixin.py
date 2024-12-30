from sqlalchemy import func, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from .id_mixin import IDMixin


class RecordMixin(IDMixin):
    """
    Mixin providing a created_at and updated_at record, which subclasses IDMixin.
    """

    _created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    _updated_at: Mapped[DateTime] = mapped_column(
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
