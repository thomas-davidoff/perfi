import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Transaction, Account, User, Category
from app.schemas import (
    DbTransactionSchema,
    DbTransactionCreateSchema,
    DbTransactionUpdateSchema,
)
from app.models.account import AccountType
from app.models.category import CategoryType
from decimal import Decimal
import uuid
from datetime import datetime, date, timezone


class TestTransaction:
    async def test_create_transaction_from_schema(
        self, session, account, expense_category
    ):
        transaction_data = DbTransactionCreateSchema(
            account_id=account.uuid,
            category_id=expense_category.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            date=date(2023, 1, 15),
            is_pending=False,
            notes="Weekly groceries",
        )

        transaction = Transaction(**transaction_data.model_dump())
        session.add(transaction)
        await session.flush()

        assert isinstance(transaction.uuid, uuid.UUID)
        assert isinstance(transaction.created_at, datetime)
        assert transaction.updated_at is None
        assert transaction.account_id == account.uuid
        assert transaction.category_id == expense_category.uuid
        assert transaction.amount == Decimal("-50.25")
        assert transaction.description == "Grocery shopping"
        assert transaction.date == date(2023, 1, 15)
        assert transaction.is_pending is False
        assert transaction.notes == "Weekly groceries"

    async def transaction_requires_valid_category(self, session, category):
        transaction_data = DbTransactionCreateSchema(
            category_id=category.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            date=date(2023, 1, 15),
            is_pending=False,
            account_id=uuid.uuid4(),
        )

        async with session.begin_nested():
            transaction = Transaction(
                **transaction_data.model_dump(exclude={"category_id"})
            )
            session.add(transaction)
            with pytest.raises(IntegrityError, match="violates not-null constraint"):
                await session.flush()

        async with session.begin_nested():
            transaction = Transaction(**transaction_data.model_dump())
            session.add(transaction)
            with pytest.raises(IntegrityError, match="violates foreign key constraint"):
                await session.flush()

    async def test_transaction_requires_valid_account(self, session, expense_category):
        transaction_data = DbTransactionCreateSchema(
            category_id=expense_category.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            date=date(2023, 1, 15),
            is_pending=False,
            account_id=uuid.uuid4(),
        )

        async with session.begin_nested():
            transaction = Transaction(
                **transaction_data.model_dump(exclude={"account_id"})
            )
            session.add(transaction)
            with pytest.raises(IntegrityError, match="violates not-null constraint"):
                await session.flush()

        async with session.begin_nested():
            transaction = Transaction(**transaction_data.model_dump())
            session.add(transaction)
            with pytest.raises(IntegrityError, match="violates foreign key constraint"):
                await session.flush()

    async def test_transaction_requires_amount(self, session, account):
        transaction_data = DbTransactionCreateSchema(
            account_id=account.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            date=date(2023, 1, 15),
            is_pending=False,
        )

        transaction = Transaction(**transaction_data.model_dump(exclude={"amount"}))
        session.add(transaction)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_transaction_requires_description(self, session, account):
        transaction_data = DbTransactionCreateSchema(
            account_id=account.uuid,
            amount=Decimal("-50.25"),
            date=date(2023, 1, 15),
            is_pending=False,
            description="Grocery shopping",
        )

        transaction = Transaction(
            **transaction_data.model_dump(exclude={"description"})
        )
        session.add(transaction)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_transaction_requires_date(self, session, account):
        transaction_data = DbTransactionCreateSchema(
            account_id=account.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            is_pending=False,
            date=date(2023, 1, 15),
        )

        transaction = Transaction(**transaction_data.model_dump(exclude={"date"}))
        session.add(transaction)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_transaction_update_with_schema(
        self, session, account, expense_category
    ):
        transaction_data = DbTransactionCreateSchema(
            account_id=account.uuid,
            category_id=expense_category.uuid,
            amount=Decimal("-50.25"),
            description="Grocery shopping",
            date=date(2023, 1, 15),
            is_pending=True,
        )

        transaction = Transaction(**transaction_data.model_dump())
        session.add(transaction)
        await session.flush()

        initial_created_at = transaction.created_at
        assert transaction.updated_at is None

        update_data = DbTransactionUpdateSchema(
            amount=Decimal("-75.50"), is_pending=False, notes="Updated notes"
        )

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(transaction, field, value)

        session.add(transaction)
        await session.flush()

        assert transaction.amount == Decimal("-75.50")
        assert transaction.is_pending is False
        assert transaction.notes == "Updated notes"
        assert isinstance(transaction.updated_at, datetime)
        assert transaction.updated_at > initial_created_at
        assert transaction.created_at == initial_created_at

    async def test_schema_validation(self):
        transaction_schema = DbTransactionSchema(
            uuid=uuid.uuid4(),
            account_id=uuid.uuid4(),
            amount=Decimal("-100.00"),
            description="Test Transaction",
            date=date(2023, 1, 1),
            created_at=datetime.now(timezone.utc),
            category_id=uuid.uuid4(),
        )

        transaction_dict = transaction_schema.model_dump()
        transaction_schema2 = DbTransactionSchema(**transaction_dict)
        assert transaction_schema.account_id == transaction_schema2.account_id
        assert transaction_schema.amount == transaction_schema2.amount
        assert transaction_schema.description == transaction_schema2.description
        assert transaction_schema.date == transaction_schema2.date

    def test_repr(self):
        transaction = Transaction(
            description="Test Transaction",
            amount=Decimal("-100.00"),
            date=date(2023, 1, 1),
        )
        assert (
            repr(transaction) == "<Transaction Test Transaction $-100.00 on 2023-01-01>"
        )
