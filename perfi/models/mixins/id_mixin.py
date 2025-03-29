from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID
from uuid import uuid4


class IDMixin:
    """Mixin providing a UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
