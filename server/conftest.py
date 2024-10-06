# conftest.py

import pytest
from extensions import db
import os


os.environ["FLASK_ENV"] = "testing"


@pytest.fixture
def app():
    from app import create_app
    from database import seed_all

    app = create_app()

    with app.app_context():
        db.create_all()
        seed_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
