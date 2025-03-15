# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import UUID, DateTime, func
# from uuid import uuid4
# from db.base import PerfiModel, PerfiSchema


# class BaseModel(DeclarativeBase):
#     id: Mapped[UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid4
#     )

#     _created_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True), default=func.now(), nullable=False
#     )

#     _updated_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True),
#         onupdate=func.now(),
#         nullable=True,
#     )

#     @property
#     def created_at(self):
#         return self._created_at

#     @created_at.setter
#     def created_at(self, value):
#         raise AttributeError("created_at is read-only.")

#     @property
#     def updated_at(self):
#         return self._updated_at

#     @updated_at.setter
#     def updated_at(self, value):
#         raise AttributeError("updated_at is read-only.")
