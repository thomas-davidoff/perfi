from .base import Repository
from database import User
from extensions import db


class UserRepository(Repository):
    @staticmethod
    def get_by_username_or_email(username_or_email) -> User:
        return (
            db.session.query(User)
            .filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
            .first()
        )
