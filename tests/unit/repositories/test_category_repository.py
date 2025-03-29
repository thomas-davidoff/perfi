import pytest
from app.exc import NotFoundException
from app.repositories import CategoryRepository
from app.models import CategoryCreateSchema, CategoryUpdateSchema, CategoryType
from tests.utils import faker
from uuid import uuid4


class TestCategoryCrud:
    async def test_create_user_category(self, session, user):
        test_category = CategoryCreateSchema(
            user_id=user.uuid,
            name=faker.word(),
            category_type=CategoryType.EXPENSE,
        )

        category = await CategoryRepository.create(session, test_category)

        assert category.uuid is not None
        assert category.created_at is not None
        assert category.updated_at is None
        assert category.name == test_category.name
        assert category.category_type == test_category.category_type
        assert category.is_system is False
        assert category.user_id == user.uuid

    async def test_create_system_category(self, session):
        test_category = CategoryCreateSchema(
            name=faker.word(),
            category_type=CategoryType.INCOME,
            is_system=True,
        )

        category = await CategoryRepository.create(session, test_category)

        assert category.uuid is not None
        assert category.user_id is None
        assert category.is_system is True

    async def test_get_category_by_id(self, session, expense_category):
        retrieved = await CategoryRepository.get_one_by_id(
            session, expense_category.uuid
        )

        assert retrieved is not None
        assert retrieved.uuid == expense_category.uuid
        assert retrieved.name == expense_category.name

    async def test_get_many_categories(
        self, session, expense_category, income_category, system_category
    ):
        categories = await CategoryRepository.get_many_by_ids(session)

        assert len(categories) >= 3
        category_uuids = [c.uuid for c in categories]
        assert expense_category.uuid in category_uuids
        assert income_category.uuid in category_uuids
        assert system_category.uuid in category_uuids

    async def test_update_category(self, session, expense_category):
        new_name = faker.word()
        update_data = CategoryUpdateSchema(
            name=new_name, category_type=CategoryType.INCOME
        )

        updated = await CategoryRepository.update_by_id(
            session, id_=expense_category.uuid, data=update_data
        )

        assert updated.name == new_name
        assert updated.category_type == CategoryType.INCOME
        assert updated.updated_at is not None

    async def test_update_nonexistent_category(self, session):
        update_data = CategoryUpdateSchema(name=faker.word())

        with pytest.raises(NotFoundException):
            await CategoryRepository.update_by_id(
                session, id_=uuid4(), data=update_data
            )

    async def test_remove_category(self, session, expense_category):
        result = await CategoryRepository.remove_by_id(session, expense_category.uuid)
        assert result == 1

        retrieved = await CategoryRepository.get_one_by_id(
            session, expense_category.uuid
        )
        assert retrieved is None

    async def test_remove_nonexistent_category(self, session):
        result = await CategoryRepository.remove_by_id(session, uuid4())
        assert result == 0

    async def test_update_many_categories(
        self, session, expense_category, income_category
    ):
        updates = {
            expense_category.uuid: CategoryUpdateSchema(
                name="Updated Expense Category"
            ),
            income_category.uuid: CategoryUpdateSchema(name="Updated Income Category"),
        }

        result = await CategoryRepository.update_many_by_ids(
            session, updates=updates, return_models=True
        )

        assert len(result) == 2

        # Verify updates were applied
        for updated_category in result:
            if updated_category.uuid == expense_category.uuid:
                assert updated_category.name == "Updated Expense Category"
            elif updated_category.uuid == income_category.uuid:
                assert updated_category.name == "Updated Income Category"
