import pytest
import pytest_asyncio
from uuid import UUID
from datetime import datetime
from perfi.models import AccountType
from tests.factories import UserFactory, AccountFactory


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    return await UserFactory.create(db_session)


@pytest.mark.asyncio
async def test_account_id_creation(db_session, test_user):
    """Test that an account gets a UUID automatically after being added to the session."""

    account = await AccountFactory.create(
        db_session, user=test_user, add_and_flush=False
    )

    # Before adding to the session, ID should be None
    assert account.id is None

    # Add to session and flush to get the default values
    db_session.add(account)
    await db_session.flush()

    # Now ID should be set
    assert account.id is not None
    assert isinstance(account.id, UUID)


@pytest.mark.asyncio
async def test_account_timestamps(db_session, test_user):
    """Test that created_at and updated_at are set automatically after being added to the session."""

    account = await AccountFactory.create(db_session, user=test_user)

    # After flushing, timestamps should be set
    assert account._created_at is not None
    assert account._updated_at is not None
    assert isinstance(account._created_at, datetime)
    assert isinstance(account._updated_at, datetime)


@pytest.mark.asyncio
async def test_account_relationships(db_session, test_user):
    """Test account relationships with user and transactions."""

    account = await AccountFactory.create(
        db_session, user=test_user, account_type=AccountType.CHECKING
    )

    # Test user relationship (should be eagerly loaded with lazy="selectin")
    assert account.user_id == test_user.id

    # The transactions relationship should exist but be empty
    assert hasattr(account, "transactions")
    assert len(account.transactions) == 0


@pytest.mark.asyncio
async def test_account_type_enum(db_session, test_user):
    """Test that account_type is properly stored as an enum."""
    # Create accounts with different types
    checking_account = await AccountFactory.create(
        db_session, user=test_user, account_type=AccountType.CHECKING
    )

    savings_account = await AccountFactory.create(
        db_session, user=test_user, account_type=AccountType.SAVINGS
    )

    credit_account = await AccountFactory.create(
        db_session, user=test_user, account_type=AccountType.CREDIT_CARD
    )

    # Verify enum values are stored correctly
    assert checking_account.account_type == AccountType.CHECKING
    assert savings_account.account_type == AccountType.SAVINGS
    assert credit_account.account_type == AccountType.CREDIT_CARD

    # Test that we can compare with string values (case-insensitive)
    assert checking_account.account_type.value == "checking"
    assert savings_account.account_type.value == "savings"
    assert credit_account.account_type.value == "credit_card"
