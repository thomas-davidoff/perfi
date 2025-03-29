from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.orm import Mapped, mapped_column
from app.models import PerfiSchema


class utcnow(FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=utcnow(),
        sort_order=9999,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        onupdate=lambda: datetime.now(timezone.utc),
        sort_order=10000,
    )


class TimestampMixinSchema(PerfiSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None
