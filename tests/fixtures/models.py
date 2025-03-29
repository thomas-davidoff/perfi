import pytest
from decimal import Decimal

from sqlalchemy.ext.asyncio.session import AsyncSession
from app.models import User, Account, AccountType, Category, CategoryType, Transaction
from tests.utils import faker
from datetime import date


@pytest.fixture
async def user(session: AsyncSession):
    user = User(
        username=faker.user_name(),
        email=faker.email(),
        hashed_password=b"not_real_hash",
    )
    session.add(user)
    await session.flush()
    return user


@pytest.fixture
async def account(session: AsyncSession, user: User):
    account = Account(
        user_id=user.uuid,
        name="First Account Checking",
        account_type=AccountType.CHECKING,
        balance=Decimal("1000.00"),
    )
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def second_account(session: AsyncSession, user: User):
    account = Account(
        user_id=user.uuid,
        name="Savings Second Account",
        account_type=AccountType.SAVINGS,
        balance=Decimal("10000.00"),
    )
    session.add(account)
    await session.flush()
    return account


@pytest.fixture
async def expense_category(session: AsyncSession, user: User):
    category = Category(
        name="Test Category",
        category_type=CategoryType.EXPENSE,
        user_id=user.uuid,
        is_system=False,
    )
    session.add(category)
    await session.flush()
    return category


@pytest.fixture
async def income_category(session: AsyncSession, user: User):
    """Create and return an income test category for the user."""
    category = Category(
        name="Salary Category",
        category_type=CategoryType.INCOME,
        user_id=user.uuid,
        is_system=False,
    )
    session.add(category)
    await session.flush()
    return category


@pytest.fixture
async def system_category(session: AsyncSession):
    """Create and return a system category with no user."""
    category = Category(
        name="System Category",
        category_type=CategoryType.EXPENSE,
        is_system=True,
    )
    session.add(category)
    await session.flush()
    return category


@pytest.fixture
async def transaction(
    session: AsyncSession, account: Account, expense_category: Category
):
    """Create and return a test transaction."""
    transaction = Transaction(
        account_id=account.uuid,
        category_id=expense_category.uuid,
        amount=Decimal("50.25"),
        description="Test Transaction",
        date=date.today(),
    )
    session.add(transaction)
    await session.flush()
    return transaction
