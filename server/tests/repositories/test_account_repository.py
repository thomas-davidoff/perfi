import pytest
from flask import Flask
from database import Account
from perfi.repositories import AccountRepository
from sqlalchemy.exc import (
    StatementError,
    IntegrityError,
)
import uuid

account_repository = AccountRepository()


def test_get_by_id_success(app: Flask, account_factory):
    account = account_factory.create()
    # it successfully retrieves an account by ID and returns an Account instance
    a = account_repository.get_by_id(account.id)
    assert isinstance(a, Account)


def test_get_by_id_no_result(app):
    account = account_repository.get_by_id(uuid.uuid4())
    assert account is None


@pytest.mark.parametrize("id", ["some string", {}, account_repository])
def test_get_by_id_invalid_id(app, id):
    with pytest.raises(Exception):
        account = account_repository.get_by_id(id)


def test_create_success(app, account_factory):
    """
    it succeeds in creating a valid account.
    """
    account = account_factory.get("valid")
    a = account_repository.create(account)
    assert isinstance(a, Account)


def test_create_invalid_category(app: Flask, account_factory):
    """
    it fails to create an account of an invalid type.
    """
    # creates an invalid transaction
    transaction = account_factory.get(variant="invalid_account_type")
    with pytest.raises(StatementError):
        # failed enum validation raises LookupError > KeyError > StatmentError
        t = account_repository.create(transaction)


def test_create_missing_name(app: Flask, account_factory):
    """
    it fails to create an account of an invalid type.
    """
    # creates a valid transaction
    transaction = account_factory.get(variant="missing_name")
    with pytest.raises(IntegrityError):
        t = account_repository.create(transaction)
