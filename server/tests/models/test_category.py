import pytest
from sqlalchemy import select
from app.models.category import Category, CategoryType
from sqlalchemy.exc import StatementError


class TestCategory:
    @pytest.mark.asyncio
    async def test_create_category(self, session):
        category = Category(
            name="Groceries",
            category_type=CategoryType.EXPENSE,
            color="#00FF00",
            icon="shopping-cart",
        )
        session.add(category)
        await session.flush()

        assert category.id is not None
        assert category.name == "Groceries"
        assert category.category_type == CategoryType.EXPENSE
        assert category.color == "#00FF00"
        assert category.icon == "shopping-cart"
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

    # @pytest.mark.asyncio
    # async def test_category_system_flag(self, session):
    #     # Create a system category
    #     system_category = await CategoryFactory.create(
    #         session,
    #         name="System Category",
    #         is_system=True
    #     )

    #     # Create a user category
    #     user_category = await CategoryFactory.create(
    #         session,
    #         name="User Category",
    #         is_system=False
    #     )

    #     # Verify system flag was set correctly
    #     assert system_category.is_system is True
    #     assert user_category.is_system is False

    #     # Query system categories
    #     query = select(Category).where(Category.is_system == True)
    #     result = await session.execute(query)
    #     system_categories = result.scalars().all()

    #     assert len(system_categories) >= 1
    #     assert any(cat.id == system_category.id for cat in system_categories)

    # @pytest.mark.asyncio
    # async def test_create_default_categories(self, session):
    #     # Create default categories
    #     default_categories = await CategoryFactory.create_default_categories(session)

    #     # Verify default categories were created
    #     assert len(default_categories) > 0

    #     # Check for expected categories
    #     income_categories = [cat for cat in default_categories if cat.category_type == CategoryType.INCOME]
    #     expense_categories = [cat for cat in default_categories if cat.category_type == CategoryType.EXPENSE]
    #     transfer_categories = [cat for cat in default_categories if cat.category_type == CategoryType.TRANSFER]

    #     assert len(income_categories) > 0
    #     assert len(expense_categories) > 0
    #     assert len(transfer_categories) == 1

    #     # Verify all are system categories
    #     assert all(cat.is_system for cat in default_categories)
