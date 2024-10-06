import pytest
from flask import Flask
from database import User
from app.repositories import UserRepository


def test_get_by_username_or_email(app: Flask):
    with app.app_context():
        # successfully returns user by username
        # remember to seed data
        user = UserRepository.get_by_username_or_email("moo_deng")
        assert isinstance(user, User)

        # does not return a non-existent user
        user = UserRepository.get_by_username_or_email("NOT A REAL USERNAME")
        assert user is None

        # successfully returns user by email
        user = UserRepository.get_by_username_or_email("moodeng@thezoo.com")
        assert isinstance(user, User)

        # does not return a non-existent user by email
        user = UserRepository.get_by_username_or_email("moodeng@asjkdnakjsndkjansd.com")
        assert user is None
