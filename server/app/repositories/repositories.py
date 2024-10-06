from .base import Repository
from database import User
from extensions import db
from typing import List
from app import logger
from sqlalchemy.exc import IntegrityError, NoResultFound


class UserRepository(Repository):
    def __init__(self) -> None:
        super().__init__()

    def get_by_id(self, id) -> User | None:
        """
        Gets a user by ID

        :param id:
            The id of the user object
        :return User:
            User object or None
        """
        user = db.session.query(User).filter(User.id == id).one_or_none()
        if user is None:
            logger.error(f"No user with ID {id} exists.")
            raise NoResultFound("No user with ID {id} exists.")
        return user

    @staticmethod
    def get_by_username_or_email(username_or_email) -> User:
        return (
            db.session.query(User)
            .filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
            .first()
        )

    def create(self, user: User) -> User:
        """Creates a valid user."""
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            logger.error(f"Integrity error when attempting to create {user}")
            db.session.rollback()
            raise

    def get_all(self) -> List[User]:
        """Gets all users"""
        return db.session.query(User).all()

    def delete(self, id) -> None:
        """Deletes a user by ID"""
        user = self.get_by_id(id)
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            logger.error(f"No user with ID {id} exists.")
            raise NoResultFound(f"No user with ID {id} exists.")
