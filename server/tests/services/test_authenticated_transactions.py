import pytest
from flask import Flask
from app.services import create_authenticated_transaction_service
from tests.helpers import TransactionFactory, UserFactory, AccountFactory
from app.exceptions import ValidationError
from pprint import pprint


# invalid transaction amount results in validation error
@pytest.mark.parametrize("amount", [123.345, "", "ajsnd", None])
def test_create_transaction_invalid_amount(app: Flask, transaction_factory, amount):

    transaction_data = transaction_factory.get("valid")

    transaction_data.update({"amount": amount})

    pprint(transaction_data)

    user_id = transaction_factory.user_id

    transaction_service = create_authenticated_transaction_service(user_id=user_id)

    with pytest.raises(ValidationError):
        transaction_service.create_transaction(transaction_data)


# invalid transaction amount results in validation error
@pytest.mark.parametrize("amount", [123, 123.45, 0, -12, 234.4])
def test_create_transaction_valid_amount(app: Flask, transaction_factory, amount):

    transaction_data = transaction_factory.get("valid")

    transaction_data.update({"amount": amount})

    pprint(transaction_data)

    user_id = transaction_factory.user_id

    transaction_service = create_authenticated_transaction_service(user_id=user_id)
    transaction_service.create_transaction(transaction_data)
