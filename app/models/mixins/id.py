from uuid import UUID as UuidType
from sqlalchemy.dialects.postgresql import UUID as UuidColumn
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4


class UuidMixin:
    uuid: Mapped[UuidType] = mapped_column(
        "uuid",
        UuidColumn(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        sort_order=-1000,
    )
