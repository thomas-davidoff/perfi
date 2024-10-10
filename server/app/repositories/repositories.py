from .base import Repository
from database import User, Transaction
from extensions import db
from typing import List
from app import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, IdentifierError


class TransactionRepository(Repository[Transaction]):
    def __init__(self) -> None:
        super().__init__(entity_name="transaction", model=Transaction)

    def get_by_id(self, id) -> Transaction | None:
        """
        Gets a transaction by ID

        :param id:
            The id of the transaction object
        :return Transaction:
            Transaction object or None
        """
        if id > 2147483647 or id < -2147483647:
            raise IdentifierError("transaction id must be of int size")
        user = db.session.query(Transaction).filter(Transaction.id == id).one_or_none()
        if user is None:
            logger.error(f"No transaction with ID {id} exists.")
            raise NoResultFound("No transaction with ID {id} exists.")
        return user

    def create(self, transaction: Transaction) -> Transaction:
        """Creates a valid transaction."""
        return super().create(entity=transaction)

    def get_all(self):
        """Retrieve all transactions"""
        return db.session.query(Transaction).all()

    def get_between_dates(self):
        """Retrieve all transactions that are between dates"""

    def bulk_delete(self, ids: List[int]) -> List[int]:
        """Bulk delete transactions by their IDs."""
        try:
            transactions_to_delete = (
                db.session.query(Transaction).filter(Transaction.id.in_(ids)).all()
            )
            if not transactions_to_delete:
                logger.warning("No transactions were deleted.")
                return []

            for transaction in transactions_to_delete:
                db.session.delete(transaction)

            db.session.commit()
            return [t.id for t in transactions_to_delete]

        except IntegrityError as e:
            db.session.rollback()  # Rollback on failure
            logger.error(f"Error during bulk delete: {e}")
            raise e

        except Exception as e:
            db.session.rollback()  # Ensure rollback for any other exceptions
            logger.error(f"Unexpected error during bulk delete: {e}")
            raise e

    def update(self, id: int, entity: Transaction) -> Transaction:
        raise NotImplementedError
        return super().update(id, entity)


class UserRepository(Repository[User]):
    def __init__(self) -> None:
        super().__init__(entity_name="user", model=User)

    def get_by_id(self, id: int) -> User | None:
        """
        Gets a user by ID

        :param id:
            The id of the user
        :return user:
            User instance or None
        """
        return super().get_by_id(id)

    @staticmethod
    def get_by_username_or_email(username_or_email) -> User:
        return (
            db.session.query(User)
            .filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
            .first()
        )

    def update(self, id: int, entity: User) -> User:
        raise NotImplementedError
        return super().update(id, entity)

    def bulk_delete(self, ids: List[int]) -> List[int]:
        raise NotImplementedError
        return super().bulk_delete(ids)

    def get_all(self) -> List[User]:
        """Gets all users"""
        return db.session.query(User).all()
