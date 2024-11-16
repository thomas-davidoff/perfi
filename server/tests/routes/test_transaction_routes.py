from flask.testing import FlaskClient
from app.services import create_user_service, UserService
from database import Transaction


user_service: UserService = create_user_service()


def test_get_all_transactions(
    client: FlaskClient, valid_user, auth_headers, transaction_factory
):
    # create 10 transactions
    transaction_factory.bulk_create(["valid"] * 10)

    accounts = user_service.get_user_accounts(valid_user.id)
    account_id_list = [str(a.id) for a in accounts]

    r = client.get(
        "/transactions/",
        headers=auth_headers,
    )
    transactions = r.json
    assert isinstance(transactions, list)
    assert len(transactions) == 10
    assert all([isinstance(t, dict) for t in transactions])
    assert all([t.get("account_id") in account_id_list for t in transactions])
