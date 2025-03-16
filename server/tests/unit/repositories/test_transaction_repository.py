from sqlite3 import IntegrityError
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.exc import IntegrityConflictException, NotFoundException
from app.repositories import TransactionRepository
from app.models import TransactionCreateSchema, TransactionUpdateSchema
from tests.utils import faker
from uuid import uuid4


class TestTransactionCrud:
    async def test_create_transaction(self, session, account, expense_category):
        test_transaction = TransactionCreateSchema(
            account_id=account.uuid,
            category_id=expense_category.uuid,
            amount=Decimal("50.25"),
            description=faker.sentence(),
            date=date.today(),
            is_pending=False,
            notes=faker.paragraph(),
        )

        transaction = await TransactionRepository.create(session, test_transaction)

        assert transaction.uuid is not None
        assert transaction.created_at is not None
        assert transaction.updated_at is None
        assert transaction.account_id == test_transaction.account_id
        assert transaction.category_id == test_transaction.category_id
        assert transaction.amount == test_transaction.amount
        assert transaction.description == test_transaction.description
        assert transaction.date == test_transaction.date
        assert transaction.is_pending == test_transaction.is_pending
        assert transaction.notes == test_transaction.notes

    async def test_create_transaction_invalid_account(self, session, expense_category):
        test_transaction = TransactionCreateSchema(
            account_id=uuid4(),  # Invalid account ID
            category_id=expense_category.uuid,
            amount=Decimal("50.25"),
            description=faker.sentence(),
            date=date.today(),
        )

        with pytest.raises(IntegrityConflictException):
            await TransactionRepository.create(session, test_transaction)

    async def test_create_transaction_invalid_category(self, session, account):
        test_transaction = TransactionCreateSchema(
            account_id=account.uuid,
            category_id=uuid4(),  # Invalid category ID
            amount=Decimal("50.25"),
            description=faker.sentence(),
            date=date.today(),
        )

        with pytest.raises(IntegrityConflictException):
            await TransactionRepository.create(session, test_transaction)

    async def test_get_transaction_by_id(self, session, transaction):
        retrieved = await TransactionRepository.get_one_by_id(session, transaction.uuid)

        assert retrieved is not None
        assert retrieved.uuid == transaction.uuid
        assert retrieved.amount == transaction.amount
        assert retrieved.description == transaction.description

    async def test_get_nonexistent_transaction(self, session):
        retrieved = await TransactionRepository.get_one_by_id(session, uuid4())
        assert retrieved is None

    async def test_update_transaction(self, session, transaction, income_category):
        new_amount = Decimal("75.50")
        new_description = faker.sentence()
        new_date = date.today() - timedelta(days=1)

        update_data = TransactionUpdateSchema(
            amount=new_amount,
            description=new_description,
            date=new_date,
            is_pending=True,
            category_id=income_category.uuid,
        )

        updated = await TransactionRepository.update_by_id(
            session, id_=transaction.uuid, data=update_data
        )

        assert updated.amount == new_amount
        assert updated.description == new_description
        assert updated.date == new_date
        assert updated.is_pending is True
        assert updated.category_id == income_category.uuid
        assert updated.updated_at is not None

    async def test_update_nonexistent_transaction(self, session):
        update_data = TransactionUpdateSchema(amount=Decimal("100.00"))

        with pytest.raises(NotFoundException):
            await TransactionRepository.update_by_id(
                session, id_=uuid4(), data=update_data
            )

    async def test_remove_transaction(self, session, transaction):
        result = await TransactionRepository.remove_by_id(session, transaction.uuid)
        assert result == 1

        retrieved = await TransactionRepository.get_one_by_id(session, transaction.uuid)
        assert retrieved is None

    async def test_remove_nonexistent_transaction(self, session):
        result = await TransactionRepository.remove_by_id(session, uuid4())
        assert result == 0

    async def test_create_multiple_transactions(
        self, session, account, expense_category, income_category
    ):
        transactions_data = [
            TransactionCreateSchema(
                account_id=account.uuid,
                category_id=(
                    expense_category.uuid if i % 2 == 0 else income_category.uuid
                ),
                amount=Decimal(f"{50 + i}.25"),
                description=f"Test Transaction {i}",
                date=date.today() - timedelta(days=i),
            )
            for i in range(5)
        ]

        for data in transactions_data:
            await TransactionRepository.create(session, data)

        all_transactions = await TransactionRepository.get_many_by_ids(session)

        assert len(all_transactions) >= 5

        descriptions = [t.description for t in all_transactions]
        for i in range(5):
            assert f"Test Transaction {i}" in descriptions
