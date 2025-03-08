from perfi.models import Transaction
from .faker import faker


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
