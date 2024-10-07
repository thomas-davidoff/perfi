import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import decode_token
import os

HEADERS = {"Content-type": "application/json", "Accept": "application/json"}
seed_pass = os.environ.get("DB_SEEDS_PASSWORD")


def test_login(client: FlaskClient):
    # valid access token is successfully returned by providing valid credentials
    r = client.post(
        "/auth/login",
        json={"username": "moo_deng", "password": seed_pass},
        headers=HEADERS,
    )
    assert r.status_code == 200
    assert "access_token" in r.json
    assert isinstance(decode_token(r.json["access_token"]), dict)
    assert decode_token(r.json["access_token"])["type"] == "access"

    # a 401 unauthorized is returned by providing invalid credentials
    r = client.post(
        "/auth/login",
        json={"username": "moo_deng", "password": "test"},
        headers=HEADERS,
    )
    assert r.status_code == 401
    # an empty payload returns a 400
    r = client.post("/auth/login", data={}, headers=HEADERS)
    assert r.status_code == 400

    # a GET returns a 405
    r = client.get("/auth/login")
    assert r.status_code == 405


def test_authorization(client: FlaskClient):
    # a 401 is returned when accessing a protected route without token
    r = client.get("/whoami", headers=HEADERS)
    assert r.status_code == 401
    # a 422 is returned when accessing a protected route with invalid token
    temp_token = "notatoken"
    headers = {**HEADERS, "Authorization": f"Bearer {temp_token}"}
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 422
    # TODO: a 401 is returned when accessing a protected route with an expired token

    # get an access token
    r = client.post(
        "/auth/login",
        json={"username": "moo_deng", "password": seed_pass},
        headers=HEADERS,
    )
    token = r.json["access_token"]
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # a 200 is returned when accessing a protected route with valid token
    r = client.get("/whoami", headers=headers)
    assert r.status_code == 200
    assert r.json == {"email": "moodeng@thezoo.com", "id": 1, "username": "moo_deng"}
