from faker import Faker
from app.models import (
    User,
    Account,
    AccountType,
    RefreshToken,
    Transaction,
    Category,
    CategoryType,
)
from abc import ABC, abstractmethod
import random
from decimal import Decimal
from datetime import datetime, timedelta

faker = Faker()


class Factory(ABC):
    @classmethod
    async def add_to_db(cls, session, entity):
        session.add(entity)
        await session.flush()

    @classmethod
    @abstractmethod
    async def create(session, add_to_db):
        raise NotImplementedError("Subclasses must implement this method.")


class UserFactory(Factory):
    @classmethod
    async def create(
        cls,
        session=None,
        username=None,
        email=None,
        password=None,
        bypass_hashing=True,
        add_to_db=True,
    ):
        if username is None:
            username = faker.user_name()
        if email is None:
            email = faker.email()
        if password is None:
            password = faker.password(length=8)
        if not session and add_to_db:
            raise Exception("Must pass session object when adding to session.")
        kwargs = dict(username=username, email=email)
        if bypass_hashing:
            kwargs[
                "_password_hash"
            ] = b"$2b$12$mockhashedvalue000000000000000000000000000000000000"
        else:
            kwargs["password"] = password
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        user = User(**kwargs)
        if add_to_db:
            if session is None:
                raise Exception("Must supply db session if adding to db.")
            await cls.add_to_db(session, user)
        return user


class AccountFactory(Factory):
    @classmethod
    async def create(
        cls,
        session=None,
        user: User = None,
        name=None,
        account_type=None,
        balance=None,
        institution=None,
        add_to_db=True,
    ):
        if name is None:
            name = random.choice(
                ["my Checking account", "my Savings Account", "My Credit card"]
            )
        if account_type is None:
            account_type = random.choice([t for t in AccountType])

        if balance is None:
            balance = Decimal(str(round(random.randint(0, 10000) / 100, 2)))

        if institution is None:
            institution = faker.company()
        if not user:
            user = await UserFactory.create(session, bypass_hashing=True)

        kwargs = dict(
            user_id=user.id,
            name=name,
            account_type=account_type,
            balance=balance,
            institution=institution,
        )

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        account = Account(**kwargs)
        if add_to_db:
            if session is None:
                raise Exception("Must supply db session if adding to db.")
            await cls.add_to_db(session, account)
        return account


class RefreshTokenFactory(Factory):
    @classmethod
    async def create(
        cls,
        session=None,
        user: User = None,
        token_value=None,
        expires_at=None,
        last_used_at=None,
        device_info=None,
        revoked=None,
        revoked_at=None,
        add_to_db=True,
    ):

        if token_value is None:
            token_value = faker.uuid4()

        if expires_at is None:
            expires_at = datetime.now() + timedelta(days=7)

        if not user:
            user = await UserFactory.create(session, bypass_hashing=True)

        kwargs = dict(
            user_id=user.id,
            token_value=token_value,
            expires_at=expires_at,
            last_used_at=last_used_at,
            device_info=device_info,
            revoked=revoked,
            revoked_at=revoked_at,
        )

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        token = RefreshToken(**kwargs)
        if add_to_db:
            if session is None:
                raise Exception("Must supply db session if adding to db.")
            await cls.add_to_db(session, token)
        return token


class TransactionFactory(Factory):
    @classmethod
    async def create(
        cls,
        session=None,
        account=None,
        category: Category = None,
        amount: Decimal = None,
        description=None,
        date=None,
        is_pending=None,
        add_to_db=True,
    ):
        if account is None:
            account = await AccountFactory.create(session)

        if amount is None:
            # amount = Decimal(str(round(random.randint(0, 500) / 100, 2)))
            amount = Decimal("100000")

        if description is None:
            description = faker.paragraph(2)

        if date is None:
            date = faker.date_this_month(before_today=True)

        kwargs = dict(
            account_id=account.id,
            amount=amount,
            description=description,
            date=date,
            is_pending=is_pending,
        )

        if category is not None:
            kwargs["category_id"] = category.id

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        transaction = Transaction(**kwargs)
        if add_to_db:
            if session is None:
                raise Exception("Must supply db session if adding to db.")
            await cls.add_to_db(session, transaction)
        return transaction


class CategoryFactory(Factory):
    @classmethod
    async def create(
        cls,
        session=None,
        name=None,
        category_type=None,
        color=None,
        icon=None,
        is_system=None,
        add_to_db=True,
    ):

        if name is None:
            name = random.choice(["Groceries"])

        if category_type is None:
            category_type = CategoryType.EXPENSE

        kwargs = dict(
            name=name,
            category_type=category_type,
            color=color,
            icon=icon,
            is_system=is_system,
        )

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        category = Category(**kwargs)
        if add_to_db:
            if session is None:
                raise Exception("Must supply db session if adding to db.")
            await cls.add_to_db(session, category)
        return category
