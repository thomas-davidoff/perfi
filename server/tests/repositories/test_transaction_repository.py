import pytest
from flask import Flask
from database import User, Transaction
from app.repositories import TransactionRepository
from sqlalchemy.exc import (
    NoResultFound,
    IdentifierError,
    IntegrityError,
)
from datetime import datetime
from extensions import db


transaction_repository = TransactionRepository()


def test_get_by_id(app: Flask, valid_transaction):
    with app.app_context():
        # Case: Returns a transaction object when the transaction with the given ID exists
        db.session.add(valid_transaction)
        db.session.commit()
        t = transaction_repository.get_by_id(1)
        assert isinstance(t, Transaction)

        # Case: Raises NoResultFound when the ID does not exist
        with pytest.raises(NoResultFound):
            t = transaction_repository.get_by_id(999)
        # # Edge Case: Handling of invalid or non-integer ID input (e.g., a string or special characters)
        # with pytest.raises(ValueError):
        #     value = '\\exit'
        # t = transaction_repository.get_by_id(value)
        # Edge Case: Handling when the ID is a valid integer but outside the possible range of IDs
        with pytest.raises(IdentifierError):
            t = transaction_repository.get_by_id(2147483648)


def test_create(app: Flask):
    with app.app_context():
        # Case: Successfully creates a transaction and returns the transaction object
        t = {
            "amount": 100,
            "description": "",
            "merchant": "test_merchant",
            "date": datetime(2020, 9, 25),
            "category": "HOUSING",
        }
        transaction = Transaction(**t)
        transaction_repository.create(transaction)
        assert isinstance(transaction, Transaction)

        # Case: Raises IntegrityError when a duplicate transaction (same ID) is inserted

        t = {
            "id": 1,
            "amount": 100,
            "description": "",
            "merchant": "test_merchant",
            "date": datetime(2020, 9, 25),
            "category": "HOUSING",
        }
        transaction = Transaction(**t)
        with pytest.raises(IntegrityError):
            transaction_repository.create(transaction)

        # Case: Raises IntegrityError if required fields (e.g., amount, date) are missing
        t = {
            "description": "",
            "merchant": "test_merchant",
            "date": datetime(2020, 9, 25),
        }
        transaction = Transaction(**t)
        with pytest.raises(IntegrityError):
            transaction_repository.create(transaction)


def test_delete(app: Flask):
    with app.app_context():
        # Case: Successfully deletes a transaction when a valid transaction ID is provided
        t = {
            "amount": 100,
            "description": "",
            "merchant": 1,
            "date": datetime(2020, 9, 25),
            "category": "HOUSING",
        }
        transaction = Transaction(**t)
        transaction = transaction_repository.create(transaction)
        deleted = transaction_repository.delete(transaction.id)
        assert isinstance(deleted, int)
        # Case: Raises NoResultFound when trying to delete a transaction with a non-existent ID
        with pytest.raises(NoResultFound):
            transaction_repository.delete(transaction.id)


def test_bulk_delete(app: Flask):
    with app.app_context():
        # Case: Successfully delete multiple valid transactions
        transactions = [
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
        ]

        created_transactions_ids = []
        for t in transactions:
            created = transaction_repository.create(Transaction(**t))
            created_transactions_ids.append(created.id)

        deleted = transaction_repository.bulk_delete(created_transactions_ids)
        assert isinstance(deleted, list)
        assert all([isinstance(d, int) for d in deleted])
        # Case: Handle an empty list of IDs
        deleted = transaction_repository.bulk_delete([])
        assert isinstance(deleted, list)
        assert len(deleted) == 0
        # Case: Handle non-existent transaction IDs

        deleted = transaction_repository.bulk_delete([99999, 100000])
        assert isinstance(deleted, list)
        assert len(deleted) == 0
        # Case: Partial success - delete valid transactions, skip non-existent ones
        transactions = [
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
            {
                "amount": 100,
                "description": "",
                "merchant": 1,
                "date": datetime(2020, 9, 25),
                "category": "HOUSING",
            },
        ]
        created_transactions_ids = []
        for t in transactions:
            created = transaction_repository.create(Transaction(**t))
            created_transactions_ids.append(created.id)
        deleted = transaction_repository.bulk_delete(
            [*created_transactions_ids, 100000]
        )

        assert 100000 not in deleted
        assert len(deleted) == 3
        for id in created_transactions_ids:
            with pytest.raises(NoResultFound):
                transaction_repository.get_by_id(id)

        # TODO: Case: Rollback all changes if an error occurs mid-operation

        # TODO: Case: Handle invalid ID formats (e.g., non-integer, None)

        pass


def test_get_all(app: Flask):
    with app.app_context():
        # Case: Returns a list of transaction objects when transactions exist
        transactions = transaction_repository.get_all()
        assert isinstance(transactions, list)
        assert all([isinstance(t, Transaction) for t in transactions])
        # Case: Returns an empty list when no transactions exist

        ids = [t.id for t in transactions]
        transaction_repository.bulk_delete(ids)

        transactions = transaction_repository.get_all()
        assert isinstance(transactions, list)
        assert len(transactions) == 0


def test_get_within_dates(app: Flask):
    with app.app_context():
        # Case: Returns transactions that fall within the given date range
        # Case: Returns an empty list if no transactions fall within the date range
        # Edge Case: Start date and end date are the same, check if transactions on that date are included
        # Edge Case: Start date is after the end date (should return an error or empty result)
        # Edge Case: Dates provided in different formats (e.g., ISO, string, datetime object)
        pass


def test_update(app: Flask):
    with app.app_context():
        # Case: Successfully updates the transaction and returns the updated transaction object
        # Case: Raises NoResultFound when trying to update a transaction with a non-existent ID
        # Edge Case: Partial updates (only updating one field like `amount` without affecting others)
        # Edge Case: Trying to update a field with an invalid value (e.g., negative transaction amount)
        # Edge Case: Attempt to update read-only fields (if any, such as creation date)
        pass
