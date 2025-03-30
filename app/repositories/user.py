from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSchema, UserCreateSchema, UserUpdateSchema
from app.exc import NotFoundException, IntegrityConflictException
from app.repositories.base import RepositoryFactory
from app.utils.password import hash_password


class UserRepository(RepositoryFactory(User)):
    @classmethod
    async def create_many(cls, *args, **kwargs) -> list[User]:
        raise NotImplementedError("Create many not implemented for users.")

    @classmethod
    async def update_many_by_ids(cls, *args, **kwargs) -> list[User] | bool:
        raise NotImplementedError("Update many not implemented for users.")

    @classmethod
    def format_user_with_password(cls, user: UserCreateSchema) -> UserSchema:
        user_data = user.model_dump()
        password = user_data.pop("password")
        db_user = UserSchema(**user_data, hashed_password=hash_password(password))
        return db_user

    @classmethod
    async def create(cls, session: AsyncSession, data: UserCreateSchema) -> User:
        db_user = cls.format_user_with_password(data)
        return await super(cls, cls).create(session, data=db_user)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> User | None:
        """Get a user by email."""

        db_model = await cls.get_one_by_id(
            session, id_=email, column="email", with_for_update=False
        )
        return db_model

    @classmethod
    async def update_by_id(
        cls,
        session: AsyncSession,
        data: UserUpdateSchema,
        id_: str | UUID,
        column: str = "uuid",
    ) -> User:
        db_model = await cls.get_one_by_id(
            session, id_, column=column, with_for_update=True
        )
        if not db_model:
            raise NotFoundException(
                f"{User.__tablename__} id={id_} not found.",
            )

        values = data.model_dump(exclude_unset=True, exclude={"password"})
        for k, v in values.items():
            setattr(db_model, k, v)

        if data.password is not None:
            db_model.hashed_password = hash_password(data.password)

        try:
            await session.commit()
            await session.refresh(db_model)
            return db_model
        except IntegrityError as e:
            raise IntegrityConflictException(
                f"{User.__tablename__} {column}={id_} conflict with existing data.",
            ) from e
