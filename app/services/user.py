from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.models.user import UserCreateSchema
from app.exc import IntegrityConflictException, UserExistsException
from pydantic import EmailStr, TypeAdapter


class UserService:
    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: UserCreateSchema):
        try:
            # First check if user exists by email
            existing_user = await cls.get_user_by_email(session, user_data.email)
            if existing_user:
                raise UserExistsException(
                    f"User with email {user_data.email} already exists"
                )

            # Create user
            user = await UserRepository.create(session=session, data=user_data)
            return user
        except IntegrityConflictException as e:
            raise UserExistsException(f"Failed to create user: {str(e)}") from e

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: str):
        email = TypeAdapter(EmailStr).validate_strings(email)
        user = await UserRepository.get_by_email(session=session, email=email.lower())
        return user
