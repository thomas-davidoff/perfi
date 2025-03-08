import pytest
import pytest_asyncio
from uuid import UUID
import json
from perfi.models import TransactionsFile, TransactionsFileImportStatus
from tests.factories import UserFactory, AccountFactory, TransactionsFileFactory


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    return await UserFactory.create(db_session)


@pytest.mark.asyncio
async def test_transactions_file_id_creation(db_session):
    """Test that a transactions file gets a UUID automatically after being added to the session."""
    transactions_file = await TransactionsFileFactory.create(
        db_session, add_and_flush=False  # todo
    )

    # Before adding to the session, ID should be None
    assert transactions_file.id is None

    # Add to session and flush to get the default values
    db_session.add(transactions_file)
    await db_session.flush()

    # Now ID should be set
    assert transactions_file.id is not None
    assert isinstance(transactions_file.id, UUID)


@pytest.mark.asyncio
async def test_transactions_file_status_property(db_session):
    """Test the status property getter and setter."""
    transactions_file = await TransactionsFileFactory.create(db_session)

    # Test the status getter
    assert transactions_file.status == "PENDING"

    # Test the status setter with string
    transactions_file.status = "processing"  # lowercase to test case insensitivity
    await db_session.flush()

    assert transactions_file._status == TransactionsFileImportStatus.PROCESSING
    assert transactions_file.status == "PROCESSING"

    # Test with invalid status
    with pytest.raises(ValueError):
        transactions_file.status = "INVALID_STATUS"


@pytest.mark.asyncio
async def test_transactions_file_json_fields(db_session):
    """Test JSON fields in the transactions file model."""
    # Create a transactions file with JSON data
    preview_data = [
        {"amount": 100.0, "description": "Test 1", "date": "2023-01-01"},
        {"amount": 200.0, "description": "Test 2", "date": "2023-01-02"},
    ]

    mapped_headers = {"Amount": "amount", "Description": "description", "Date": "date"}

    error_log = ["Error 1", "Error 2"]

    transactions_file = await TransactionsFileFactory.create(
        db_session,
        preview_data=preview_data,
        mapped_headers=mapped_headers,
        error_log=error_log,
    )

    # Test that JSON fields are stored and retrieved correctly
    assert json.loads(transactions_file.preview_data) == preview_data
    assert json.loads(transactions_file.mapped_headers) == mapped_headers
    assert json.loads(transactions_file.error_log) == error_log


@pytest.mark.asyncio
async def test_transactions_file_relationships(db_session, test_user):
    """Test transactions file relationships with user and transactions."""

    transactions_file = await TransactionsFileFactory.create(db_session, user=test_user)

    # Test user relationship
    assert transactions_file.user_id == test_user.id

    # The transactions relationship should exist but be empty
    assert hasattr(transactions_file, "transactions")
    assert len(transactions_file.transactions) == 0
