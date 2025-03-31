import pytest
from decimal import Decimal
from app.exc import NotFoundException
from app.repositories import AccountRepository
from app.models import AccountType
from tests.utils import faker
from uuid import uuid4
from app.schemas import AccountCreateSchema, AccountUpdateSchema


class TestAccountRepository:
    async def test_create_account(self, session, user):
        test_account = AccountCreateSchema(
            user_id=user.uuid,
            name=faker.company(),
            account_type=AccountType.CHECKING,
            balance=Decimal("100.50"),
            institution=faker.company(),
            description=faker.sentence(),
        )

        account = await AccountRepository.create(session, test_account)

        assert account.uuid is not None
        assert account.created_at is not None
        assert account.updated_at is None
        assert account.name == test_account.name
        assert account.account_type == test_account.account_type
        assert account.balance == test_account.balance
        assert account.institution == test_account.institution
        assert account.description == test_account.description
        assert account.is_active is True
        assert account.user_id == user.uuid

    async def test_get_account_by_id(self, session, user, account):
        retrieved = await AccountRepository.get_one_by_id(session, account.uuid)

        assert retrieved is not None
        assert retrieved.uuid == account.uuid
        assert retrieved.name == account.name
        assert retrieved.user_id == user.uuid

    async def test_get_nonexistent_account(self, session):
        retrieved = await AccountRepository.get_one_by_id(session, uuid4())
        assert retrieved is None

    async def test_get_many_by_ids(self, session, account, second_account):
        accounts = await AccountRepository.get_many_by_ids(
            session, ids=[account.uuid, second_account.uuid]
        )

        assert len(accounts) == 2
        account_uuids = [a.uuid for a in accounts]
        assert account.uuid in account_uuids
        assert second_account.uuid in account_uuids

    async def test_update_account(self, session, account):
        new_name = faker.company()
        new_balance = Decimal("250.75")
        update_data = AccountUpdateSchema(
            name=new_name, balance=new_balance, is_active=False
        )

        updated = await AccountRepository.update_by_id(
            session, id_=account.uuid, data=update_data
        )

        assert updated.name == new_name
        assert updated.balance == new_balance
        assert updated.is_active is False
        assert updated.account_type == account.account_type  # Unchanged
        assert updated.updated_at is not None

    async def test_update_nonexistent_account(self, session):
        update_data = AccountUpdateSchema(name=faker.company())

        with pytest.raises(NotFoundException):
            await AccountRepository.update_by_id(session, id_=uuid4(), data=update_data)

    async def test_remove_account(self, session, account):
        result = await AccountRepository.remove_by_id(session, account.uuid)
        assert result == 1

        retrieved = await AccountRepository.get_one_by_id(session, account.uuid)
        assert retrieved is None

    async def test_remove_nonexistent_account(self, session):
        result = await AccountRepository.remove_by_id(session, uuid4())
        assert result == 0

    async def test_update_many_by_ids(self, session, account, second_account):
        updates = {
            account.uuid: AccountUpdateSchema(name="Updated First Account"),
            second_account.uuid: AccountUpdateSchema(name="Updated Second Account"),
        }

        result = await AccountRepository.update_many_by_ids(
            session, updates=updates, return_models=True
        )

        assert len(result) == 2

        # Verify updates were applied
        for updated_account in result:
            if updated_account.uuid == account.uuid:
                assert updated_account.name == "Updated First Account"
            elif updated_account.uuid == second_account.uuid:
                assert updated_account.name == "Updated Second Account"

    async def test_remove_many_by_ids(self, session, account, second_account):
        result = await AccountRepository.remove_many_by_ids(
            session, ids=[account.uuid, second_account.uuid]
        )

        assert result == 2

        # Verify accounts were removed
        accounts = await AccountRepository.get_many_by_ids(
            session, ids=[account.uuid, second_account.uuid]
        )
        assert len(accounts) == 0
