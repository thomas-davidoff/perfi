from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from perfi.core.repositories.base import AsyncRepository
from perfi.core.database.models import User
from sqlalchemy.exc import NoResultFound
import logging

logger = logging.getLogger(__name__)


class UserRepository(AsyncRepository[User]):
    def __init__(self) -> None:
        super().__init__(entity_name="user", model=User)

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[User]:
        """
        Gets a user by ID.

        :param session: Async database session
        :param id: The ID of the user
        :return: User instance or None
        """
        return await super().get_by_id(session, id)

    async def get_by_username_or_email(
        self, session: AsyncSession, username_or_email: str
    ) -> Optional[User]:
        """
        Gets a user by their username or email.

        :param session: Async database session
        :param username_or_email: The username or email to search for
        :return: User instance or None
        """
        query = select(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update_by_id(self, session: AsyncSession, id: int, data: dict) -> User:
        """
        Updates a user in the database.

        :param session: Async database session
        :param id: The ID of the user
        :param data: Dictionary of fields to update
        :return: Updated User instance
        """
        return await super().update_by_id(session, id, data)

    async def bulk_delete(self, session: AsyncSession, ids: List[int]) -> List[int]:
        """
        Deletes multiple users by their IDs.

        :param session: Async database session
        :param ids: List of IDs to delete
        :return: List of deleted IDs
        """
        deleted_ids = []
        for id in ids:
            try:
                await self.delete(session, id)
                deleted_ids.append(id)
            except NoResultFound:
                logger.warning(
                    f"Skipping delete of user id {id} because it does not exist."
                )
                continue
        return deleted_ids

    async def get_all(self, session: AsyncSession) -> List[User]:
        """
        Gets all users.

        :param session: Async database session
        :return: List of User instances
        """
        return await super().get_all(session)

    async def create(self, session: AsyncSession, data: dict) -> User:
        """
        Creates a new user in the database.

        :param session: Async database session
        :param data: Dictionary of user fields
        :return: Created User instance
        """
        return await super().create(session, data)
