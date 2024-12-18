import pytest
from flask import Flask
from database import Transaction
from app.repositories import TransactionRepository
from sqlalchemy.exc import (
    NoResultFound,
    StatementError,
    IntegrityError,
    SAWarning,
    ArgumentError,
)
from extensions import db
from datetime import datetime
import warnings
import uuid
from app.exceptions import ResourceNotFoundError

transaction_repository = TransactionRepository()


def test_get_by_id(app: Flask, transaction_factory):
    # create a valid transaction
    transaction = transaction_factory.create("valid")

    # Case: Returns a transaction object when the transaction with the given ID exists
    print(transaction)
    t = transaction_repository.get_by_id(transaction.id)
    assert isinstance(t, Transaction)


def test_get_by_id_no_result(app: Flask):
    # get a non-existent transaction
    t = transaction_repository.get_by_id(uuid.uuid4())
    assert t is None


def test_get_by_id_not_uuid(app: Flask):
    with pytest.raises(ArgumentError):
        transaction_repository.get_by_id(1)


def test_create_success(app: Flask, transaction_factory):
    # creates a valid transaction
    transaction = transaction_factory.get()
    t = transaction_repository.create(transaction)
    assert isinstance(t, Transaction)
    assert isinstance(t.id, uuid.UUID)


def test_create_invalid_category(app: Flask, transaction_factory):
    # creates a valid transaction
    transaction = transaction_factory.get(variant="invalid_category")
    with pytest.raises(StatementError):
        t = transaction_repository.create(transaction)


def test_create_invalid_date(app: Flask, transaction_factory):
    # creates a valid transaction
    transaction = transaction_factory.get(variant="invalid_date")
    with pytest.raises(StatementError):
        t = transaction_repository.create(transaction)


def test_create_missing_amount(app: Flask, transaction_factory):
    # creates a valid transaction
    transaction = transaction_factory.get(variant="missing_amount")
    with pytest.raises(IntegrityError):
        t = transaction_repository.create(transaction)


def test_create_missing_account_id(app: Flask, transaction_factory):
    # creates a valid transaction
    transaction = transaction_factory.get(variant="missing_account_id")
    with pytest.raises(IntegrityError):
        t = transaction_repository.create(transaction)


def test_create_duplicate_id(app: Flask, transaction_factory):
    # creates a valid transaction
    t = transaction_factory.get(variant="valid")
    t = transaction_repository.create(t)

    with pytest.raises(IntegrityError):

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=SAWarning)
            new_t = {**transaction_factory.get("valid"), **{"id": t.id}}
            t = transaction_repository.create(new_t)


def test_delete(app: Flask, transaction_factory):
    t = transaction_factory.create()
    # Case: Successfully deletes a transaction when a valid transaction ID is provided
    deleted = transaction_repository.delete(t.id)
    assert isinstance(deleted, uuid.UUID)
    assert db.session.get(Transaction, t.id) is None
    # Case: Raises NoResultFound when trying to delete a transaction with a non-existent ID
    with pytest.raises(ResourceNotFoundError):
        transaction_repository.delete(t.id)


def test_bulk_delete_success(app: Flask, transaction_factory):
    transactions = transaction_factory.bulk_create(["valid"] * 5)
    # Case: Successfully delete multiple valid transactions

    deleted = transaction_repository.bulk_delete([t.id for t in transactions])
    assert isinstance(deleted, list)
    assert all([isinstance(d, uuid.UUID) for d in deleted])


def test_bulk_delete_empty_list(app: Flask):
    # Case: Successfully delete multiple valid transactions

    deleted = transaction_repository.bulk_delete([])
    assert isinstance(deleted, list)
    assert len(deleted) == 0


def test_bulk_delete_non_existent(app: Flask):
    # Case: Successfully delete multiple valid transactions
    deleted = transaction_repository.bulk_delete([uuid.uuid4()] * 3)
    assert isinstance(deleted, list)
    assert len(deleted) == 0


def test_bulk_delete_skip_invalid(app: Flask, transaction_factory):
    count = 5
    transactions = transaction_factory.bulk_create(["valid"] * count)
    # Case: Successfully delete multiple valid transactions

    deleted = transaction_repository.bulk_delete(
        [*[t.id for t in transactions], uuid.uuid4()]
    )
    assert isinstance(deleted, list)
    assert len(deleted) == 5
    assert 100 not in deleted

    for id in deleted:
        assert db.session.get(Transaction, id) is None


def test_get_all_success(app: Flask, transaction_factory):
    count = 5
    transaction_factory.bulk_create(["valid"] * count)

    transactions = transaction_repository.get_all()
    # Case: Returns a list of transaction objects when transactions exist
    assert transactions
    assert isinstance(transactions, list)
    assert all([isinstance(t, Transaction) for t in transactions])
    assert len(transactions) == count


def test_get_all_none_found(app: Flask):
    # Case: Returns an empty list when no transactions exist
    transactions = transaction_repository.get_all()
    assert isinstance(transactions, list)
    assert len(transactions) == 0


def test_get_between_dates_success(app: Flask, transaction_factory):
    transactions = transaction_factory.bulk_create(variants=["valid"] * 5)
    # Case: Returns transactions that fall within the given date range
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    transactions = transaction_repository.get_between_dates(start_date, end_date)
    print(transactions)
    assert isinstance(transactions, list)
    assert all([isinstance(t, Transaction) for t in transactions])
    assert all([start_date <= t.date and end_date >= t.date] for t in transactions)


def test_get_between_dates_no_transactions(app: Flask):
    # Case: Returns an empty list if no transactions fall within the date range
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    transactions = transaction_repository.get_between_dates(start_date, end_date)
    assert isinstance(transactions, list)
    assert not transactions


def test_get_between_dates_improper_range(app: Flask):
    # Edge Case: Start date is after the end date (should return an error or empty result)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    with pytest.raises(ValueError):
        transactions = transaction_repository.get_between_dates(end_date, start_date)


def test_get_between_dates_single_day_range(app: Flask, transaction_factory):
    transaction = transaction_factory.create("valid")
    transaction_datetime = transaction.date
    # Edge Case: Start date and end date are the same, check if transactions on that date are included
    transactions = transaction_repository.get_between_dates(
        transaction_datetime, transaction_datetime
    )

    assert transactions
    assert isinstance(transactions, list)
    assert all([isinstance(t, Transaction) for t in transactions])
    assert all(
        [transaction_datetime <= t.date and transaction_datetime >= t.date]
        for t in transactions
    )
    assert len(transactions) == 1


def test_update_success(app: Flask, transaction_factory):
    transaction = transaction_factory.create("valid")
    # update the amount to 200
    updated = transaction_repository.update(transaction.id, {"amount": 200})
    assert isinstance(transaction, Transaction)
    assert updated.id == transaction.id
    assert updated.amount == 200


def test_update_invalid_category(app: Flask, transaction_factory):
    transaction = transaction_factory.create("valid")
    # update the amount to 200
    with pytest.raises(StatementError):
        updated = transaction_repository.update(
            transaction.id, {"category": "NOT A REAL CATEGORY"}
        )


def test_update_non_existent(app: Flask):
    # try to update a non-existent id
    with pytest.raises(ResourceNotFoundError):
        transaction_repository.update(uuid.uuid4(), {})


def test_update_write_only_field(app: Flask, transaction_factory):
    t = transaction_factory.create()
    with pytest.raises(AttributeError):
        transaction_repository.update(t.id, {"created_at": datetime(2024, 10, 10)})
