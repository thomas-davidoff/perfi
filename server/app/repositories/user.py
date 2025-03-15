import bcrypt
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSchema, UserCreateSchema, UserUpdateSchema
from app.exc import NotFoundException, IntegrityConflictException
from app.repositories.base import CrudFactory

from app.utils.password import hash_password


class UserCrud(CrudFactory(User)):
    @classmethod
    async def create_many(cls, *args, **kwargs) -> list[User]:
        raise NotImplementedError("Create many not implemented for users.")

    @classmethod
    async def update_many_by_ids(cls, *args, **kwargs) -> list[User] | bool:
        raise NotImplementedError("Update many not implemented for users.")

    @classmethod
    def format_user_with_password(cls, user: UserCreateSchema) -> UserSchema:
        """Take a Pydantic UserCreateSchema and return a UserSchema with the password
        hashed.

        Args:
            user (UserCreateSchema): Pydantic UserCreateSchema holding the user information

        Returns:
            UserSchema: Pydantic UserSchema with the password hashed
        """
        user_data = user.model_dump()
        password = user_data.pop("password")
        db_user = UserSchema(**user_data, hashed_password=hash_password(password))
        return db_user

    # @classmethod
    # def get_password_hash(cls, password: str) -> bytes:
    # pwd_bytes = password.encode("utf-8")
    # salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
    # return bcrypt.hashpw(password=pwd_bytes, salt=salt)

    @classmethod
    async def create(cls, session: AsyncSession, data: UserCreateSchema) -> User:
        """Create a user in the database. This method is overridden to hash the password
        and then calls the parent create method, with the hashed password.

        Args:
            session (AsyncSession): SQLAlchemy async session
            data (UserCreateSchema): Pydantic UserCreateSchema holding the user information

        Returns:
            User: SQLAlchemy User model
        """
        db_user = cls.format_user_with_password(data)
        return await super(cls, cls).create(session, data=db_user)

    @classmethod
    async def update_by_id(
        cls,
        session: AsyncSession,
        data: UserUpdateSchema,
        id_: str | UUID,
        column: str = "uuid",
    ) -> User:
        """Updates a user in the database based on a column value and returns the
        updated user. Raises an exception if the user isn't found or if the column
        doesn't exist.

        Overrides the parent method to hash the password if it is included in the
        update.

        Args:
            session (AsyncSession): SQLAlchemy async session
            data (UserUpdateSchema): Pydantic schema for the updated data.
            id_ (str | UUID): value to search for in `column`
            column (str, optional): the column name in which to search.
                Defaults to "uuid".

        Raises:
            NotFoundException: user not found in database given id_ and column
            IntegrityConflictException: update conflicts with existing data

        Returns:
            User: updated SQLAlchemy model
        """
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
