from extensions import db
from sqlalchemy import func


class TimestampMixin(object):
    # NOW() AT TIME ZONE \'UTC\' is postgresql specific.
    # However, it ensures ts will be created in utc time without having to call python datetime
    # created_at = db.Column(
    #     db.DateTime(timezone=True), default=text("NOW() AT TIME ZONE 'UTC'")
    # )
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
