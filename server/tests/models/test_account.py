import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import StatementError
from app.models import Account, AccountType, User
import uuid


class TestAccount:
    @pytest.mark.asyncio
    async def test_create_account(self, session, db_user):
        account = Account(
            user_id=db_user.id,
            name="Checking Account",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000.00"),
            institution="Test Bank",
        )
        session.add(account)
        await session.flush()

        # Verify account was created successfully
        assert account.id is not None
        assert isinstance(account.id, uuid.UUID)
        assert account.name == "Checking Account"
        assert account.account_type == AccountType.CHECKING
        assert account.balance == Decimal("1000.00")
        assert account.institution == "Test Bank"
        assert account.user_id == db_user.id

    @pytest.mark.asyncio
    async def test_account_type_validation(self, session, db_user):
        for account_type in AccountType:
            account = Account(
                user_id=db_user.id,
                name=f"Test {account_type.name}",
                account_type=account_type,
                balance=Decimal("0.00"),
            )
            session.add(account)
            await session.flush()
            assert account.id is not None
            assert account.account_type == account_type

        session.expunge_all()

        async with session.begin_nested():
            with pytest.raises(
                StatementError,
                match="'INVALID_TYPE' is not among the defined enum values",
            ):
                account = Account(
                    user_id=db_user.id,
                    name="Invalid Account",
                    account_type="INVALID_TYPE",
                    balance=Decimal("0.00"),
                )
                session.add(account)
                await session.flush()


class TestAccountRelationships:
    """Tests for RefreshToken relationships"""

    async def test_account_user_relationship(self, session, db_user, db_account):

        # Test relationship from account to user
        assert db_account.user is not None
        assert db_account.user.id == db_user.id

        query = (
            select(User)
            .options(selectinload(User.accounts))
            .where(User.id == db_user.id)
        )
        result = await session.execute(query)
        user_with_accounts = result.scalars().first()

        assert user_with_accounts is not None
        assert len(user_with_accounts.accounts) == 1
        assert user_with_accounts.accounts[0].id == db_account.id

    async def delete_user_deletes_account(self, session, db_user, db_account):
        query = (
            select(Account)
            .options(selectinload(Account.user))
            .where(Account.id == db_account.id)
        )
        before = await session.execute(query)
        assert before.scalars().first() is db_account

        await session.delete(db_user)
        await session.commit()

        after = await session.execute(query)
        assert after.scalars().first() is None
