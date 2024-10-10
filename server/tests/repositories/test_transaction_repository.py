import pytest
from flask import Flask
from database import User, Transaction
from app.repositories import TransactionRepository
from sqlalchemy.exc import (
    NoResultFound,
    IdentifierError,
    StatementError,
    IntegrityError,
    SAWarning,
)
from extensions import db
from typing import Callable
from datetime import datetime
import warnings

transaction_repository = TransactionRepository()


# @pytest.mark.parametrize("transaction", ["valid"], indirect=True)
def test_get_by_id(app: Flask, transaction_factory):
    with app.app_context():
        # create a valid transaction
        transaction = transaction_factory.create("valid")

        # Case: Returns a transaction object when the transaction with the given ID exists
        print(transaction)
        t = transaction_repository.get_by_id(transaction.id)
        assert isinstance(t, Transaction)

        # Case: Raises NoResultFound when the ID does not exist
        with pytest.raises(NoResultFound):
            t = transaction_repository.get_by_id(transaction.id + 1)

        # Edge Case: Handling when the ID is a valid integer but outside the possible range of IDs
        with pytest.raises(IdentifierError):
            t = transaction_repository.get_by_id(2147483648)


def test_create_success(app: Flask, transaction_factory):
    with app.app_context():
        # creates a valid transaction
        transaction = transaction_factory.get()
        t = transaction_repository.create(transaction)
        assert isinstance(t, Transaction)
        assert isinstance(t.id, int)


def test_create_invalid_category(app: Flask, transaction_factory):
    with app.app_context():
        # creates a valid transaction
        transaction = transaction_factory.get(variant="invalid_category")
        with pytest.raises(StatementError):
            t = transaction_repository.create(transaction)


def test_create_invalid_date(app: Flask, transaction_factory):
    with app.app_context():
        # creates a valid transaction
        transaction = transaction_factory.get(variant="invalid_date")
        with pytest.raises(StatementError):
            t = transaction_repository.create(transaction)


def test_create_missing_amount(app: Flask, transaction_factory):
    with app.app_context():
        # creates a valid transaction
        transaction = transaction_factory.get(variant="missing_amount")
        with pytest.raises(IntegrityError):
            t = transaction_repository.create(transaction)


def test_create_duplicate_id(app: Flask, transaction_factory):
    with app.app_context():
        # creates a valid transaction
        t = transaction_factory.get(variant="valid")
        t = transaction_repository.create(t)

        with pytest.raises(IntegrityError):

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=SAWarning)
                new_t = Transaction(
                    amount=100, merchant="test", date=datetime(2024, 10, 10), id=1
                )
                t = transaction_repository.create(new_t)


def test_delete(app: Flask, transaction_factory):
    with app.app_context():
        t = transaction_factory.create()
        # Case: Successfully deletes a transaction when a valid transaction ID is provided
        deleted = transaction_repository.delete(t.id)
        assert isinstance(deleted, int)
        assert db.session.get(Transaction, t.id) is None
        # Case: Raises NoResultFound when trying to delete a transaction with a non-existent ID
        with pytest.raises(NoResultFound):
            transaction_repository.delete(t.id)


def test_bulk_delete_success(app: Flask, transaction_factory):
    with app.app_context():
        transactions = transaction_factory.bulk_create(["valid"] * 5)
        # Case: Successfully delete multiple valid transactions

        deleted = transaction_repository.bulk_delete([t.id for t in transactions])
        assert isinstance(deleted, list)
        assert all([isinstance(d, int) for d in deleted])


def test_bulk_delete_empty_list(app: Flask):
    with app.app_context():
        # Case: Successfully delete multiple valid transactions

        deleted = transaction_repository.bulk_delete([])
        assert isinstance(deleted, list)
        assert len(deleted) == 0


def test_bulk_delete_non_existent(app: Flask):
    with app.app_context():
        # Case: Successfully delete multiple valid transactions

        deleted = transaction_repository.bulk_delete([1, 2, 3])
        assert isinstance(deleted, list)
        assert len(deleted) == 0


def test_bulk_delete_skip_invalid(app: Flask, transaction_factory):
    with app.app_context():
        count = 5
        transactions = transaction_factory.bulk_create(["valid"] * count)
        # Case: Successfully delete multiple valid transactions

        deleted = transaction_repository.bulk_delete(
            [*[t.id for t in transactions], 100]
        )
        assert isinstance(deleted, list)
        assert len(deleted) == 5
        assert 100 not in deleted

        for id in deleted:
            assert db.session.get(Transaction, id) is None


def test_get_all_success(app: Flask, transaction_factory):
    with app.app_context():
        count = 5
        transaction_factory.bulk_create(["valid"] * count)

        transactions = transaction_repository.get_all()
        # Case: Returns a list of transaction objects when transactions exist
        assert transactions
        assert isinstance(transactions, list)
        assert all([isinstance(t, Transaction) for t in transactions])
        assert len(transactions) == count


def test_get_all_none_found(app: Flask):
    with app.app_context():
        # Case: Returns an empty list when no transactions exist
        transactions = transaction_repository.get_all()
        assert isinstance(transactions, list)
        assert len(transactions) == 0


# # def test_get_within_dates_success(app: Flask):
# #     with app.app_context():
# #         # Case: Returns transactions that fall within the given date range
# #         start_date = datetime(2024, 1, 1)
# #         end_date = datetime(2024, 1, 31)
# transactions = transaction_repository.get_between_dates(start_date, end_date)
# #         assert isinstance(transactions, list)
# #         assert all([isinstance(t, Transaction) for t in transactions])
# #         assert all([start_date <= t.date and end_date >= t.date] for t in transactions)


# # def test_get_within_dates_no_transactions(app: Flask):
# #     with app.app_context():
# #         # Case: Returns an empty list if no transactions fall within the date range
# #         start_date = datetime(2024, 1, 1)
# #         end_date = datetime(2024, 1, 31)
# #         transactions = transaction_repository.get_between_dates(start_date, end_date)
# #         assert isinstance(transactions, list)
# #         assert not transactions


# # def test_get_within_dates_improper_range(app: Flask):
# #     with app.app_context():
# #         # Edge Case: Start date is after the end date (should return an error or empty result)
# #         start_date = datetime(2024, 1, 1)
# #         end_date = datetime(2024, 1, 31)
# #         with pytest.raises(ValueError):
# #             transactions = transaction_repository.get_between_dates(
# #                 end_date, start_date
# #             )


# # def test_get_within_dates_single_day_range(app: Flask):
# #     with app.app_context():
# #         # Edge Case: Start date and end date are the same, check if transactions on that date are included
# #         start_date = datetime(2024, 1, 1)
# #         end_date = datetime(2024, 1, 1)
# #         transactions = transaction_repository.get_between_dates(end_date, start_date)

# #         assert transactions
# #         assert isinstance(transactions, list)
# #         assert all([isinstance(t, Transaction) for t in transactions])
# #         assert all([start_date <= t.date and end_date >= t.date] for t in transactions)
# #         assert len(transactions) == 1

# #         # Edge Case: Dates provided in different formats (e.g., ISO, string, datetime object)
# #         pass


# def test_update(app: Flask):
#     with app.app_context():
#         # Case: Successfully updates the transaction and returns the updated transaction object
#         # Case: Raises NoResultFound when trying to update a transaction with a non-existent ID
#         # Edge Case: Partial updates (only updating one field like `amount` without affecting others)
#         # Edge Case: Trying to update a field with an invalid value (e.g., negative transaction amount)
#         # Edge Case: Attempt to update read-only fields (if any, such as creation date)
#         pass
