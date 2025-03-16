import pytest
from decimal import Decimal
from tests.factories import TransactionFactory, AccountFactory, CategoryFactory


class TestTransaction:
    async def test_create_transaction(self, session):

        account = await AccountFactory.create(session)
        category = await CategoryFactory.create(session)
        transaction = await TransactionFactory.create(
            session,
            category=category,
            account=account,
            description="test",
            amount=Decimal("12309.00"),
        )

        assert transaction.id is not None
        assert transaction.account_id == account.id
        assert transaction.category_id == category.id
        assert transaction.description == "test"
        assert transaction.amount == Decimal("12309.00")
        assert transaction.is_pending is False
