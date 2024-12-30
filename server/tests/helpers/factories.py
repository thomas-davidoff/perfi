from perfi.core.database import User, Account, Transaction
from faker import Faker

faker = Faker()


class UserFactory:
    @staticmethod
    async def create(session, **kwargs):
        user = User(
            username=kwargs.get("username", faker.user_name()),
            email=kwargs.get("email", faker.email()),
            password=kwargs.get("password", faker.password(length=9)),
        )
        session.add(user)
        await session.commit()
        return user


class AccountFactory:
    @staticmethod
    def create(session, user, **kwargs):
        account = Account(
            user_id=user.id,
            name=kwargs.get("name", faker.word()),
        )
        session.add(account)
        session.commit()
        return account


class TransactionFactory:
    @staticmethod
    def create(session, account, **kwargs):
        transaction = Transaction(
            account_id=account.id,
            amount=kwargs.get("amount", faker.random_number(digits=4)),
            description=kwargs.get("description", faker.sentence()),
        )
        session.add(transaction)
        session.commit()
        return transaction
