import pytest
from flask import Flask
from perfi.services import create_transactions_service
from perfi.exceptions import ValidationError
from pprint import pprint


# invalid transaction amount results in validation error
@pytest.mark.parametrize("amount", [123.345, "", "ajsnd", None])
def test_create_transaction_invalid_amount(app: Flask, transaction_factory, amount):

    transaction_data = transaction_factory.get("valid")

    transaction_data.update({"amount": amount})

    pprint(transaction_data)

    transaction_service = create_transactions_service()

    with pytest.raises(ValidationError):
        transaction_service.create_transaction(transaction_data)


# invalid transaction amount results in validation error
@pytest.mark.parametrize("amount", [123, 123.45, 0, -12, 234.4])
def test_create_transaction_valid_amount(app: Flask, transaction_factory, amount):

    transaction_data = transaction_factory.get("valid")

    transaction_data.update({"amount": amount})
    transaction_service = create_transactions_service()
    transaction_service.create_transaction(transaction_data)
