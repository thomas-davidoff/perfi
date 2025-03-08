import pytest
from uuid import UUID
from datetime import datetime
from perfi.models import User
from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_user_id_creation(db_session):
    """Test that a user gets a UUID automatically after being added to the session."""
    # Create a user
    user = User(
        username="testuser", email="test@example.com", _password_hash="dummy_hash"
    )

    # Before adding to the session, ID should be None
    assert user.id is None

    # Add to session and flush to get the default values
    db_session.add(user)
    await db_session.flush()

    # Now ID should be set
    assert user.id is not None
    assert isinstance(user.id, UUID)


@pytest.mark.asyncio
async def test_user_timestamps(db_session):
    """Test that created_at and updated_at are set automatically after being added to the session."""
    # Create a user
    user = User(
        username="testuser", email="test@example.com", _password_hash="dummy_hash"
    )

    # Add to session and flush
    db_session.add(user)
    await db_session.flush()

    # After flushing, timestamps should be set
    assert user._created_at is not None
    assert user._updated_at is not None
    assert isinstance(user._created_at, datetime)
    assert isinstance(user._updated_at, datetime)

    # Test read-only properties
    with pytest.raises(AttributeError):
        user.created_at = datetime.now()

    with pytest.raises(AttributeError):
        user.updated_at = datetime.now()


@pytest.mark.asyncio
async def test_password_property(db_session):
    """Test the password property setter and getter."""
    # Create a user
    user = User(username="testuser", email="test@example.com")

    # Set password through property
    user.password = "securepassword123"

    # Password hash should be set
    assert user._password_hash is not None
    assert user._password_hash != "securepassword123"  # Should be hashed

    # Password getter should raise AttributeError
    with pytest.raises(AttributeError):
        _ = user.password


@pytest.mark.asyncio
async def test_verify_password(db_session):
    """Test password verification."""
    pwd = "testpassword123"
    test_user = await UserFactory.create(db_session, password=pwd)
    # Correct password should verify
    assert test_user.verify_password(pwd) is True

    # Incorrect password should not verify
    assert test_user.verify_password("wrongpassword") is False


@pytest.mark.asyncio
async def test_user_relationships(db_session):
    """Test that user relationships are initialized as empty collections."""
    # After creating a user, the relationship collections should be empty lists
    # Note: With lazy="selectin", the relationships should be loaded automatically

    test_user = await UserFactory.create(db_session)

    # Relationships should exist but be empty
    assert hasattr(test_user, "accounts")
    assert len(test_user.accounts) == 0

    assert hasattr(test_user, "transactions_files")
    assert len(test_user.transactions_files) == 0

    assert hasattr(test_user, "refresh_tokens")
    assert len(test_user.refresh_tokens) == 0
