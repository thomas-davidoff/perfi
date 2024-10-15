import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import decode_token
import os
from tests.helpers.helpers import add_valid_user


HEADERS = {"Content-type": "application/json", "Accept": "application/json"}
seed_pass = os.environ.get("DB_SEEDS_PASSWORD")
expired_token = os.environ["EXPIRED_TOKEN"]
TEST_PASSWORD = os.environ.get("TEST_PASSWORD")


def test_login_success(client: FlaskClient, valid_user):
    # valid access token is successfully returned by providing valid credentials
    r = client.post(
        "/auth/login",
        json={"username": valid_user.username, "password": TEST_PASSWORD},
        headers=HEADERS,
    )
    assert r.status_code == 200
    assert "access_token" in r.json
    assert isinstance(decode_token(r.json["access_token"]), dict)
    assert decode_token(r.json["access_token"])["type"] == "access"


def test_login_invalid_password(client: FlaskClient, valid_user):
    # a 401 unauthorized is returned by providing invalid password
    r = client.post(
        "/auth/login",
        json={"username": valid_user.username, "password": "NOT THE PASSWORD"},
        headers=HEADERS,
    )
    assert r.status_code == 401


def test_login_invalid_username(client: FlaskClient, valid_user):
    # a 401 unauthorized is returned by providing invalid password
    r = client.post(
        "/auth/login",
        json={"username": "not the username", "password": TEST_PASSWORD},
        headers=HEADERS,
    )
    assert r.status_code == 401


def test_login_empty_payload(client: FlaskClient):
    # an empty payload returns a 400, with a helpful message
    r = client.post("/auth/login", data={}, headers=HEADERS)
    assert r.status_code == 400
    assert "error" in r.json
    assert "Invalid or missing JSON body" in r.json["error"]


def test_login_no_username(client: FlaskClient):
    # an empty payload returns a 400, with a helpful message
    r = client.post("/auth/login", json={"password": TEST_PASSWORD}, headers=HEADERS)
    assert r.status_code == 400
    assert "error" in r.json
    assert "Provide username and password" in r.json["error"]


def test_login_no_password(client: FlaskClient):
    # an empty payload returns a 400, with a helpful message
    r = client.post("/auth/login", json={"username": "test"}, headers=HEADERS)
    assert r.status_code == 400
    assert "error" in r.json
    assert "Provide username and password" in r.json["error"]


def test_login_wrong_method(client: FlaskClient):
    # a GET returns a 405
    r = client.get("/auth/login")
    assert r.status_code == 405


def test_authorization_expired_token(client: FlaskClient):
    # a 401 is returned when accessing a protected route with an expired token
    headers = {**HEADERS, "Authorization": f"Bearer {expired_token}"}
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 401


def test_authorization_no_auth(client: FlaskClient):
    # a 401 is returned when accessing a protected route without token
    r = client.get("/whoami", headers=HEADERS)
    assert r.status_code == 401


def test_authorization_invalid_token(client: FlaskClient):
    # a 422 is returned when accessing a protected route with invalid token
    temp_token = "notatoken"
    headers = {**HEADERS, "Authorization": f"Bearer {temp_token}"}
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 422


def test_authorization_success(client: FlaskClient, valid_user):
    # get an access token
    r = client.post(
        "/auth/login",
        json={"username": valid_user.username, "password": TEST_PASSWORD},
        headers=HEADERS,
    )
    token = r.json["access_token"]
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # a 200 is returned when accessing a protected route with valid token
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 200
    assert r.json == {
        "email": valid_user.email,
        "id": str(valid_user.id),
        "username": valid_user.username,
    }
