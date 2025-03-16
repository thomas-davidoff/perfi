import pytest
from decimal import Decimal
from sqlalchemy.exc import StatementError
from app.models import AccountType, User
import uuid
from tests.factories import AccountFactory, UserFactory


class TestAccount:
    async def test_create_account(self, session):
        user = await UserFactory.create(session)
        account = await AccountFactory.create(
            session,
            name="Checking account",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.00"),
            institution="test banque",
            user=user,
        )
        # Verify account was created successfully
        assert account.id is not None
        assert isinstance(account.id, uuid.UUID)
        assert account.name == "Checking account"
        assert account.account_type == AccountType.CHECKING
        assert account.balance == Decimal("1000.00")
        assert account.institution == "test banque"
        assert account.user_id == user.id

    async def test_account_type_validation(self, session):
        user = await UserFactory.create(session)
        for account_type in AccountType:
            account = await AccountFactory.create(
                session,
                account_type=account_type,
                user=user,
            )
            assert account.id is not None
            assert account.account_type == account_type

        session.expunge_all()

        async with session.begin_nested():
            with pytest.raises(
                StatementError,
                match="'INVALID_TYPE' is not among the defined enum values",
            ):
                account = await AccountFactory.create(
                    session,
                    account_type="INVALID_TYPE",
                    user=user,
                )


class TestAccountRelationships:
    """Tests for RefreshToken relationships"""

    async def test_account_user_relationship(self, session):

        user = await UserFactory.create(session)
        account = await AccountFactory.create(session, user=user)

        # Test relationship from account to user
        assert account.user is not None
        assert isinstance(account.user, User)
