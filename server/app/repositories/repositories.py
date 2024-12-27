from .base import Repository
from database import User, Transaction, Account, TransactionCategory
from extensions import db
from typing import List
from app import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, IdentifierError
from uuid import UUID
from app.utils import StandardDate


class TransactionRepository(Repository[Transaction]):
    def __init__(self) -> None:
        super().__init__(entity_name="transaction", model=Transaction)

    def get_by_id(self, id: UUID) -> Transaction | None:
        """
        Gets a transaction by ID

        :param id:
            The id of the transaction object
        :return Transaction:
            Transaction object or None
        """
        return super().get_by_id(id)

    def create(self, data: dict) -> Transaction:
        """Creates a valid transaction."""

        data_to_create = data

        provided_category = data.get("category").upper()
        if not provided_category in [c.value for c in TransactionCategory]:
            print(
                f"WARNING: category {provided_category} is not a transaction category."
            )
            data_to_create["category"] = TransactionCategory.UNCATEGORIZED.value
        return super().create(data=data_to_create)

    def get_all(self):
        """Gets all transactions"""
        return super().get_all()

    def get_between_dates(self, start_date, end_date):
        """Retrieve all transactions that are between dates"""
        start = StandardDate(start_date).date
        end = StandardDate(end_date).date

        if end < start:
            raise ValueError("start_date must be before or equal to end_date.")

        return (
            db.session.query(Transaction)
            .filter(Transaction.date.between(start, end))
            .all()
        )

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

    def update(self, id: int, data: dict) -> Transaction:
        """Creates a transaction that already exists in the database"""
        return super().update(id, data)

    def get_user_transactions(self, user_id):
        query = (
            db.session.query(Transaction)
            .join(Account)
            .filter(Account.user_id == user_id)
        )
        return query.all()

    def get_where(self, filter_data: dict):
        return db.session.query(Transaction).filter_by(**filter_data).first()


class UserRepository(Repository[User]):
    def __init__(self) -> None:
        super().__init__(entity_name="user", model=User)

    def get_by_id(self, id) -> User | None:
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

    def get_all(self):
        """Gets all users"""
        return super().get_all()

    def create(self, data):
        """Creates a user in the database."""
        return super().create(data)


class AccountRepository(Repository[Account]):
    def __init__(self):
        super().__init__("account", Account)

    def create(self, data) -> Account:
        """Creates an account in the database"""
        return super().create(data)

    def get_by_id(self, id) -> Account:
        """Gets an account by ID"""
        return super().get_by_id(id)

    def get_all(self) -> List[Account]:
        """Gets all accounts from the database"""
        return super().get_all()

    def delete(self, id) -> int:
        """Deletes an account by ID"""
        return super().delete(id)

    def bulk_delete(self, ids):
        """Deletes a list of accounts by id"""
        return super().bulk_delete(ids)

    def update(self, id, data) -> Account:
        """Updates an account by id"""
        return super().update(id, data)
