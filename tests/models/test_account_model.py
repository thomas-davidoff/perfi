import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Account, User
from app.models.account import AccountType
from app.schemas import DbAccountSchema, DbAccountCreateSchema, DbAccountUpdateSchema
from decimal import Decimal
import uuid
from datetime import datetime, timezone


class TestAccount:
    async def test_create_account_from_schema(self, session):
        user = User(
            email="test@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()

        account_data = DbAccountCreateSchema(
            user_id=user.uuid,
            name="Main Checking",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.50"),
            institution="Test Bank",
            description="My primary checking account",
            is_active=True,
        )

        account = Account(**account_data.model_dump())
        session.add(account)
        await session.flush()

        assert isinstance(account.uuid, uuid.UUID)
        assert isinstance(account.created_at, datetime)
        assert account.updated_at is None
        assert account.name == "Main Checking"
        assert account.account_type == AccountType.CHECKING
        assert account.balance == Decimal("1000.50")
        assert account.institution == "Test Bank"
        assert account.description == "My primary checking account"
        assert account.is_active is True
        assert account.user_id == user.uuid

    async def test_account_requires_user(self, session):
        account_data = DbAccountCreateSchema(
            name="Main Checking",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.50"),
            user_id=uuid.uuid4(),
        )

        account = Account(**account_data.model_dump(exclude={"user_id"}))
        session.add(account)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_account_requires_name(self, session):
        user = User(
            email="test2@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()

        account_data = DbAccountCreateSchema(
            name="Main Checking",
            user_id=user.uuid,
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.50"),
        )

        account = Account(**account_data.model_dump(exclude={"name"}))
        session.add(account)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_account_requires_account_type(self, session):
        user = User(
            email="test3@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()

        account_data = DbAccountCreateSchema(
            user_id=user.uuid,
            name="Test Account",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.50"),
        )

        account = Account(**account_data.model_dump(exclude={"account_type"}))
        session.add(account)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_account_update_with_schema(self, session):
        user = User(
            email="test4@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()

        account_data = DbAccountCreateSchema(
            user_id=user.uuid,
            name="Main Checking",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.50"),
        )
        account = Account(**account_data.model_dump())
        session.add(account)
        await session.flush()

        initial_created_at = account.created_at
        assert account.updated_at is None

        update_data = DbAccountUpdateSchema(
            balance=Decimal("2000.75"), name="Updated Checking"
        )

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(account, field, value)

        session.add(account)
        await session.flush()

        assert account.balance == Decimal("2000.75")
        assert account.name == "Updated Checking"
        assert isinstance(account.updated_at, datetime)
        assert account.updated_at > initial_created_at
        assert account.created_at == initial_created_at

    async def test_account_default_values(self, session):
        user = User(
            email="test5@example.com",
            hashed_password=b"not_real_hash",
        )
        session.add(user)
        await session.flush()

        account_data = DbAccountCreateSchema(
            user_id=user.uuid,
            name="Minimal Account",
            account_type=AccountType.SAVINGS,
        )

        account = Account(**account_data.model_dump())
        session.add(account)
        await session.flush()

        assert account.balance == Decimal("0.00")
        assert account.institution is None
        assert account.description is None
        assert account.is_active is True

    def test_schema_validation(self):
        account_schema = DbAccountSchema(
            uuid=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="Schema Test Account",
            account_type=AccountType.INVESTMENT,
            balance=Decimal("500.00"),
            created_at=datetime.now(timezone.utc),
        )
        account_dict = account_schema.model_dump()
        account_schema2 = DbAccountSchema(**account_dict)
        assert account_schema.name == account_schema2.name
        assert account_schema.account_type == account_schema2.account_type
        assert account_schema.balance == account_schema2.balance

    def test_repr(self):
        account = Account(
            name="Savings Account",
            account_type=AccountType.SAVINGS,
            balance=Decimal("5000.00"),
        )
        assert repr(account) == "<Account Savings Account (savings) balance=5000.00>"
