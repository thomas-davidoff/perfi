import pytest
from sqlalchemy import select
from app.models.category import Category, CategoryType
from sqlalchemy.exc import StatementError


class TestCategory:
    async def test_create_category(self, session):
        category = Category(
            name="Groceries",
            category_type=CategoryType.EXPENSE,
        )
        session.add(category)
        await session.flush()

        assert category.id is not None
        assert category.name == "Groceries"
        assert category.category_type == CategoryType.EXPENSE
        assert category.is_system is False

    async def test_category_type_validation(self, session):
        # Test valid category types
        for category_type in CategoryType:
            category = Category(
                name=f"Test {category_type.name}", category_type=category_type
            )
            session.add(category)
            await session.flush()
            assert category.id is not None
            assert category.category_type == category_type

        # Clear the session
        session.expunge_all()

        # Test invalid category type
        with pytest.raises(ValueError):
            category = Category(name="Invalid Category", category_type="INVALID_TYPE")

    async def test_category_type_validation(self, session):
        for category_type in CategoryType:
            category = Category(
                name=f"Test {category_type.name}", category_type=category_type
            )
            session.add(category)
            await session.flush()
            assert category.id is not None
            assert category.category_type == category_type

        session.expunge_all()

        async with session.begin_nested():
            with pytest.raises(
                StatementError,
                match="'INVALID_TYPE' is not among the defined enum values",
            ):
                category = Category(
                    name=f"Test {category_type.name}", category_type="INVALID_TYPE"
                )
                session.add(category)
                await session.flush()
