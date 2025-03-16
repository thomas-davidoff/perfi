import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Category, User
from app.models.category import (
    CategoryType,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
import uuid
from datetime import datetime, timezone
from tests.utils import faker


class TestCategory:
    async def test_create_category_with_user_from_schema(self, session, user):
        category_data = CategoryCreateSchema(
            name="Groceries",
            category_type=CategoryType.EXPENSE,
            is_system=False,
            user_id=user.uuid,
        )

        category = Category(**category_data.model_dump())
        session.add(category)
        await session.flush()

        assert isinstance(category.uuid, uuid.UUID)
        assert isinstance(category.created_at, datetime)
        assert category.updated_at is None
        assert category.name == "Groceries"
        assert category.category_type == CategoryType.EXPENSE
        assert category.is_system is False
        assert category.user_id == user.uuid

    async def test_create_system_category_without_user(self, session):
        category_data = CategoryCreateSchema(
            name="Uncategorized",
            category_type=CategoryType.EXPENSE,
            is_system=True,
        )

        category = Category(**category_data.model_dump())
        session.add(category)
        await session.flush()

        assert category.user_id is None
        assert category.is_system is True

    async def test_create_invalid_category(self, session):
        # A category with no user_id and is_system=False should raise an error
        with pytest.raises(
            ValueError,
            match="is_system must be explictly set to True if user_id is not passed",
        ):
            CategoryCreateSchema(
                name=faker.word(),
                category_type=CategoryType.INCOME,
                is_system=False,
            )

    async def test_category_requires_name(self, session, user):
        category_data = CategoryCreateSchema(
            name="Uncategorized",
            category_type=CategoryType.EXPENSE,
            is_system=False,
            user_id=user.uuid,
        )

        category = Category(**category_data.model_dump(exclude={"name"}))
        session.add(category)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_category_requires_type(self, session, user):
        category_data = CategoryCreateSchema(
            name="Uncategorized",
            category_type=CategoryType.EXPENSE,
            is_system=False,
            user_id=user.uuid,
        )
        category = Category(**category_data.model_dump(exclude={"category_type"}))
        session.add(category)
        with pytest.raises(IntegrityError, match="violates not-null constraint"):
            await session.flush()

    async def test_category_update_with_schema(self, session, user):
        category_data = CategoryCreateSchema(
            name="Entertainment",
            category_type=CategoryType.EXPENSE,
            is_system=False,
            user_id=user.uuid,
        )

        category = Category(**category_data.model_dump())
        session.add(category)
        await session.flush()

        initial_created_at = category.created_at
        assert category.updated_at is None

        update_data = CategoryUpdateSchema(name="Movies & Entertainment")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        session.add(category)
        await session.flush()

        assert category.name == "Movies & Entertainment"
        assert isinstance(category.updated_at, datetime)
        assert category.updated_at > initial_created_at
        assert category.created_at == initial_created_at

    async def test_all_category_types(self, session, user):
        for category_type in CategoryType:
            category_data = CategoryCreateSchema(
                name=f"Test {category_type.value}",
                category_type=category_type,
                is_system=False,
                user_id=user.uuid,
            )

            category = Category(**category_data.model_dump())
            session.add(category)
            await session.flush()

            assert category.category_type == category_type

    def test_repr(self):
        category = Category(
            name="Groceries",
            category_type=CategoryType.EXPENSE,
            is_system=False,
        )
        assert repr(category) == "<Category name=Groceries type=expense>"
