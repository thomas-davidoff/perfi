import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Transaction, Account, User, Category
from app.models.transaction import (
    TransactionSchema,
    TransactionCreateSchema,
    TransactionUpdateSchema,
)
from app.models.account import AccountType
from app.models.category import CategoryType
from decimal import Decimal
import uuid
from datetime import datetime, date, timezone


class TestTransaction:
    @pytest.fixture
    async def user(self, session):
        user = User(
            username="transaction_user",
            email="trans_test@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()
        return user

    @pytest.fixture
    async def account(self, session, user):
        account = Account(
            user_id=user.uuid,
            name="Test Account",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.00"),
        )
        session.add(account)
        await session.flush()
        return account

    @pytest.fixture
    async def category(self, session, user):
        category = Category(
            name="Test Category",
            category_type=CategoryType.EXPENSE,
            user_id=user.uuid,
            is_system=False,
        )
        session.add(category)
        await session.flush()
        return category

    async def test_create_transaction_from_schema(self, session, account, category):
        transaction_data = TransactionCreateSchema(
            account_id=account.uuid,
            category_id=category.uuid,
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
        assert transaction.category_id == category.uuid
        assert transaction.amount == Decimal("-50.25")
        assert transaction.description == "Grocery shopping"
        assert transaction.date == date(2023, 1, 15)
        assert transaction.is_pending is False
        assert transaction.notes == "Weekly groceries"

    async def transaction_requires_valid_category(self, session, category):
        transaction_data = TransactionCreateSchema(
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

    async def test_transaction_requires_valid_account(self, session, category):
        transaction_data = TransactionCreateSchema(
            category_id=category.uuid,
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
        transaction_data = TransactionCreateSchema(
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
        transaction_data = TransactionCreateSchema(
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
        transaction_data = TransactionCreateSchema(
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

    async def test_transaction_update_with_schema(self, session, account, category):
        transaction_data = TransactionCreateSchema(
            account_id=account.uuid,
            category_id=category.uuid,
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

        # Create update data
        update_data = TransactionUpdateSchema(
            amount=Decimal("-75.50"), is_pending=False, notes="Updated notes"
        )

        # Apply updates from schema to model
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
        # Verify schema validation works
        transaction_schema = TransactionSchema(
            uuid=uuid.uuid4(),
            account_id=uuid.uuid4(),
            amount=Decimal("-100.00"),
            description="Test Transaction",
            date=date(2023, 1, 1),
            created_at=datetime.now(timezone.utc),
            category_id=uuid.uuid4(),
        )

        # Convert to and from dict should preserve values
        transaction_dict = transaction_schema.model_dump()
        transaction_schema2 = TransactionSchema(**transaction_dict)
        assert transaction_schema.account_id == transaction_schema2.account_id
        assert transaction_schema.amount == transaction_schema2.amount
        assert transaction_schema.description == transaction_schema2.description
        assert transaction_schema.date == transaction_schema2.date

    def test_repr(self):
        # Added __repr__ method to transaction model
        transaction = Transaction(
            description="Test Transaction",
            amount=Decimal("-100.00"),
            date=date(2023, 1, 1),
        )
        assert (
            repr(transaction) == "<Transaction Test Transaction $-100.00 on 2023-01-01>"
        )
