from flask.testing import FlaskClient
from app.services import create_user_service, UserService
from database import Transaction
from sqlalchemy.orm import object_session
from pprint import pprint
import pytest
from app.exceptions import ValidationError
from uuid import uuid4


user_service: UserService = create_user_service()


def test_get_all_transactions(
    client: FlaskClient, valid_user, auth_headers, transaction_factory
):
    # create 10 transactions
    transaction_factory.bulk_create(["valid"] * 10)

    accounts = user_service.get_user_accounts(valid_user.id)
    account_id_list = [str(a.id) for a in accounts]

    r = client.get(
        "/api/transactions/",
        headers=auth_headers,
    )
    transactions = r.json
    assert isinstance(transactions, list)
    assert len(transactions) == 10
    assert all([isinstance(t, dict) for t in transactions])
    assert all([t.get("account_id") in account_id_list for t in transactions])


def test_create_transaction_success(client: FlaskClient, auth_headers, account_factory):

    account = account_factory.create("valid")
    data = {
        "account_id": account.id,
        "amount": 123.45,
        "date": "1998-09-25",
        "merchant": "nasdkjnasd",
        "category": "groceries",
    }
    r = client.post(f"/api/transactions/", json=data, headers=auth_headers)
    assert r.status_code == 201
    pprint(r.json)


@pytest.mark.parametrize(
    "data",
    [
        {
            "amount": 123.45,
            "date": "1998-09-25",
            "merchant": "nasdkjnasd",
            "category": "groceries",
        },
    ],
)
def test_create_transaction_no_account(client: FlaskClient, auth_headers, data):

    r = client.post(f"/api/transactions/", json=data, headers=auth_headers)
    assert r.status_code == 400
    pprint(r.json)


@pytest.mark.parametrize(
    "data",
    [
        {
            "amount": "hi",
            "date": "1998-09-25",
            "merchant": "nasdkjnasd",
            "category": "groceries",
        },
        {
            "amount": 123.45,
            "date": "1998-09-25",
            "category": "groceries",
        },
        {
            "amount": 123.45,
            "date": "1998-09-259",
            "merchant": "nasdkjnasd",
            "category": "groceries",
        },
        {
            "amount": 123.45,
            "date": "1998-09-25",
            "merchant": "nasdkjnasd",
            "category": "aslkdmalksdm",
        },
    ],
)
def test_create_transaction_fail_validation(
    client: FlaskClient, auth_headers, data, account_factory
):
    account = account_factory.create("valid")

    datum = {**data, "account_id": account.id}

    r = client.post(f"/api/transactions/", json=datum, headers=auth_headers)
    assert r.status_code == 400
    pprint(r.json)


def test_delete_transaction_success(
    client: FlaskClient, transaction_factory, auth_headers
):

    valid_transaction = transaction_factory.create("valid")
    # create transaction
    r = client.delete(
        f"/api/transactions/{valid_transaction.id}",
        headers=auth_headers,
    )
    assert r.status_code == 204
