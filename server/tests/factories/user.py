from app.models import User
from .faker import faker


class UserFactory:
    @staticmethod
    def create(
        username=faker.user_name(),
        email=faker.email(),
        password=faker.password(length=8),
        bypass_hashing=True,
    ):
        kwargs = dict(username=username, email=email)
        if bypass_hashing:
            kwargs[
                "_password_hash"
            ] = b"$2b$12$mockhashedvalue000000000000000000000000000000000000"
        else:
            kwargs["password"] = password
        return User(**kwargs)
