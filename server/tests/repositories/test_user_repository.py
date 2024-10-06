import pytest
from flask import Flask
from database import User
from app.repositories import UserRepository
from sqlalchemy.exc import IntegrityError, NoResultFound


user_repository = UserRepository()


def test_get_by_username_or_email(app: Flask):
    with app.app_context():
        # successfully returns user by username
        # remember to seed data
        user = user_repository.get_by_username_or_email("moo_deng")
        assert isinstance(user, User)

        # does not return a non-existent user
        user = user_repository.get_by_username_or_email("NOT A REAL USERNAME")
        assert user is None

        # successfully returns user by email
        user = user_repository.get_by_username_or_email("moodeng@thezoo.com")
        assert isinstance(user, User)

        # does not return a non-existent user by email
        user = user_repository.get_by_username_or_email(
            "moodeng@asjkdnakjsndkjansd.com"
        )
        assert user is None


def test_get_all(app: Flask):
    with app.app_context():
        # it successfully gets all users
        users = user_repository.get_all()
        assert isinstance(users, list)
        assert len(users) > 0
        assert all([isinstance(u, User) for u in users])


def test_create(app: Flask):
    with app.app_context():
        # it successfully creates a user with correct data
        user = User(username="test", password="test", email="test@test.com")
        user = user_repository.create(user)

        assert isinstance(user, User)
        assert user.username == "test"

        user_repository.delete(user.id)

        # it does not create a user with a duplicate email
        user1 = User(username="test", password="test", email="test@test.com")
        user_repository.create(user1)
        user2 = User(username="test", password="test", email="test@test.com")

        with pytest.raises(IntegrityError):
            user2 = user_repository.create(user2)

        user_repository.delete(user1.id)


def test_delete(app: Flask):
    with app.app_context():
        # create test user
        user = User(username="test", password="test", email="test@test.com")
        user = user_repository.create(user)

        # it successfully deletes the user
        user_repository.delete(user.id)

        with pytest.raises(NoResultFound):
            user_repository.get_by_id(user.id)

        # it fails to delete a non-existent id
        with pytest.raises(NoResultFound):
            user_repository.delete(999)


def test_update(app: Flask):
    with app.app_context():
        with pytest.raises(NotImplementedError):
            user_repository.update(100, "data")
