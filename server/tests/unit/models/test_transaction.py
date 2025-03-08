import pytest
from uuid import UUID
from datetime import datetime
from perfi.schemas.transaction import TransactionCategory
from perfi.models import Transaction
from tests.factories import AccountFactory


@pytest.mark.asyncio
async def test_transaction_id_creation(db_session):
    """Test that a transaction gets a UUID automatically after being added to the session."""

    test_account = await AccountFactory.create(db_session)

    # Create a transaction
    transaction = Transaction(
        amount=100.0, merchant="Test Merchant", account_id=test_account.id
    )

    # Before adding to the session, ID should be None
    assert transaction.id is None

    # Add to session and flush to get the default values
    db_session.add(transaction)
    await db_session.flush()

    # Now ID should be set
    assert transaction.id is not None
    assert isinstance(transaction.id, UUID)


@pytest.mark.asyncio
async def test_transaction_timestamps(db_session):
    """Test that created_at and updated_at are set automatically after being added to the session."""

    test_account = await AccountFactory.create(db_session)
    # Create a transaction
    transaction = Transaction(
        amount=100.0, merchant="Test Merchant", account_id=test_account.id
    )

    # Before adding to the session, timestamps might be None
    db_session.add(transaction)
    await db_session.flush()

    # After flushing, timestamps should be set
    assert transaction._created_at is not None
    assert transaction._updated_at is not None
    assert isinstance(transaction._created_at, datetime)
    assert isinstance(transaction._updated_at, datetime)

    # Test read-only properties
    with pytest.raises(AttributeError):
        transaction.created_at = datetime.now()

    with pytest.raises(AttributeError):
        transaction.updated_at = datetime.now()


@pytest.mark.asyncio
async def test_transaction_category_property(db_session):
    """Test that the category property works correctly."""

    test_account = await AccountFactory.create(db_session)
    # Create a transaction with explicit category
    transaction = Transaction(
        amount=100.0,
        merchant="Test Merchant",
        account_id=test_account.id,
        _category=TransactionCategory.ENTERTAINMENT,
    )

    db_session.add(transaction)
    await db_session.flush()

    # Check the category getter
    assert transaction.category == "ENTERTAINMENT"

    # Test setting by string
    transaction.category = "entertainment"  # lowercase should be converted to uppercase
    await db_session.flush()

    assert transaction._category == TransactionCategory.ENTERTAINMENT
    assert transaction.category == "ENTERTAINMENT"

    # Test invalid category
    with pytest.raises(ValueError):
        transaction.category = "INVALID_CATEGORY"

    # Create a transaction with default category and check if it's set after flush
    default_transaction = Transaction(
        amount=100.0, merchant="Test Merchant", account_id=test_account.id
    )

    db_session.add(default_transaction)
    await db_session.flush()

    # After flushing, the default category should be set
    assert default_transaction._category == TransactionCategory.UNCATEGORIZED
    assert default_transaction.category == "UNCATEGORIZED"


@pytest.mark.asyncio
async def test_transaction_user_id_property(db_session):
    """Test that user_id property correctly returns the account's user_id."""

    test_account = await AccountFactory.create(db_session)
    # Create a transaction linked to the test account
    transaction = Transaction(
        amount=100.0, merchant="Test Merchant", account_id=test_account.id
    )

    db_session.add(transaction)
    await db_session.flush()

    # The user_id property should return the account's user_id
    assert transaction.user_id == test_account.user_id
