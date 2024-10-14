import pytest
from flask import Flask
from database import Account
from app.repositories import AccountRepository
from sqlalchemy.exc import (
    NoResultFound,
    IdentifierError,
    StatementError,
    IntegrityError,
    SAWarning,
)
from extensions import db
from datetime import datetime
import warnings

account_repository = AccountRepository()


def test_get_by_id_success(app: Flask, account_factory):
    account = account_factory.create()

    # it successfully retrieves an account by ID and returns an Account instance
    a = account_repository.get_by_id(account.id)

    assert isinstance(a, Account)
    assert a.id == account.id
