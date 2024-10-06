from database import User
from extensions import db
import pytest
from sqlalchemy.exc import IntegrityError


def test_duplicate_email(app):
    with app.app_context():
        # duplicate email or username raises IntegrityError
        user = User(username="test", password="test", email="test@test.com")
        user2 = User(username="tes2", password="test", email="test@test.com")
        db.session.add_all([user, user2])
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_user_dump(app):
    with app.app_context():
        user = User(username="test", password="test", email="test@test.com")
        json = user.dump()
        assert isinstance(json, dict)
        assert json == {"id": None, "username": "test", "email": "test@test.com"}
