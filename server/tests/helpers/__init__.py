import functools


def with_app_context(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app = kwargs.get("app")
        if app is None:
            raise ValueError("App fixture is required but not passed to the function")

        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


from .transactions import TransactionFactory
from .accounts import AccountFactory
