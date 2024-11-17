from flask.testing import FlaskClient
from flask_jwt_extended import decode_token
import os
import pytest


HEADERS = {"Content-type": "application/json", "Accept": "application/json"}
seed_pass = os.environ.get("DB_SEEDS_PASSWORD")
expired_token = os.environ["EXPIRED_TOKEN"]


def test_login_success(client: FlaskClient, user_factory):
    # create valid user
    u = user_factory.create("valid")
    # valid access token is successfully returned by providing valid credentials
    r = client.post(
        "/api/auth/login",
        json={"username": u.username, "password": os.environ["DB_SEEDS_PASSWORD"]},
        headers=HEADERS,
    )

    assert r.status_code == 200
    assert "access_token" in r.json
    assert isinstance(decode_token(r.json["access_token"]), dict)
    assert decode_token(r.json["access_token"])["type"] == "access"


def test_login_invalid_password(client: FlaskClient, user_factory):
    # create valid user
    u = user_factory.create("valid")

    # a 401 unauthorized is returned by providing invalid password
    r = client.post(
        "/api/auth/login",
        json={"username": u.username, "password": "NOT THE PASSWORD"},
        headers=HEADERS,
    )
    assert r.status_code == 401


def test_login_invalid_username(client: FlaskClient, user_factory):
    # create valid user
    u = user_factory.create("valid")

    # a 401 unauthorized is returned by providing invalid password
    r = client.post(
        "/api/auth/login",
        json={
            "username": "not the username",
            "password": os.environ["DB_SEEDS_PASSWORD"],
        },
        headers=HEADERS,
    )
    assert r.status_code == 401


def test_login_empty_payload(client: FlaskClient):
    # an empty payload returns a 400, with a helpful message
    r = client.post("/api/auth/login", data={}, headers=HEADERS)
    print(r.text)
    assert r.status_code == 422
    assert "error" in r.json
    assert "Invalid or missing JSON body" in r.json["error"]


@pytest.mark.parametrize(
    "user_data", [{"password": os.environ["DB_SEEDS_PASSWORD"]}, {"username": "test"}]
)
def test_login_missing_data(client: FlaskClient, user_data):
    # an empty payload returns a 400, with a helpful message
    r = client.post(
        "/api/auth/login",
        json=user_data,
        headers=HEADERS,
    )
    assert r.status_code == 422
    assert "error" in r.json
    assert "Missing username or password" in r.json["error"]


def test_login_wrong_method(client: FlaskClient):
    # a GET returns a 405
    r = client.get("/api/auth/login")
    print(r.text)
    print(r.status_code)
    assert r.status_code == 405


def test_whoami_authorization_expired_token(client: FlaskClient):
    # a 401 is returned when accessing a protected route with an expired token
    headers = {**HEADERS, "Authorization": f"Bearer {expired_token}"}
    r = client.get("api/whoami", headers=headers)
    assert r.status_code == 401


def test_whoami_authorization_no_auth(client: FlaskClient):
    # a 401 is returned when accessing a protected route without token
    r = client.get("api/whoami", headers=HEADERS)
    assert r.status_code == 401


def test_whoami_authorization_invalid_token(client: FlaskClient):
    # a 422 unauthorized is returned when accessing a protected route with invalid token
    # search for `default_invalid_token_callback` in flask_jwt_extended to see why
    temp_token = "notatoken"
    headers = {**HEADERS, "Authorization": f"Bearer {temp_token}"}
    r = client.get("/api/whoami", headers=headers)
    assert r.status_code == 422


def test_whoami_authorization_success(client: FlaskClient, user_factory):
    # create valid user
    u = user_factory.create("valid")

    # get an access token
    r = client.post(
        "/api/auth/login",
        json={
            "username": u.username,
            "password": os.environ["DB_SEEDS_PASSWORD"],
        },
        headers=HEADERS,
    )
    token = r.json["access_token"]
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # a 200 is returned when accessing a protected route with valid token
    r = client.get("/api/whoami", headers=headers)
    assert r.status_code == 200
    assert r.json == {
        "email": u.email,
        "id": str(u.id),
        "username": u.username,
    }


valid_user_data = {
    "username": "takjsdn",
    "password": "kjasdkjns",
    "email": "kjansd@klasd.com",
}


def test_register_success(client: FlaskClient):

    r = client.post("/api/auth/register", json=valid_user_data, headers=HEADERS)

    assert r.status_code == 201


def test_register_user_can_log_in(client: FlaskClient):
    r = client.post("/api/auth/register", json=valid_user_data, headers=HEADERS)

    r = client.post(
        "/api/auth/login",
        json={
            "username": valid_user_data["username"],
            "password": valid_user_data["password"],
        },
        headers=HEADERS,
    )

    assert r.status_code == 200
    assert "access_token" in r.json
    assert isinstance(decode_token(r.json["access_token"]), dict)
    assert decode_token(r.json["access_token"])["type"] == "access"


def test_register_invalid_password(client: FlaskClient):

    invalid_password_data = {**valid_user_data, "password": 12345}

    r = client.post("/api/auth/register", json=invalid_password_data, headers=HEADERS)
    print(r.text)
    print(r.status_code)
    assert r.status_code == 400
    assert r.json["error"] == "Password is too simple."


def test_register_no_data(client: FlaskClient):

    r = client.post("/api/auth/register", headers=HEADERS)
    print(r.text)
    print(r.status_code)

    assert r.status_code == 422


@pytest.mark.parametrize(
    "user_data",
    [
        {"password": "kjans", "email": "kjnasd@kjns.com"},
        {"username": "1234324123", "email": "kjnasd@kjns.com"},
        {"username": "1234324123", "password": "kjansdkjnasd"},
    ],
)
def test_register_missing_data(client: FlaskClient, user_data):

    r = client.post("/api/auth/register", headers=HEADERS)
    print(r.text)
    print(r.status_code)

    assert r.status_code == 422


def test_register_user_already_exists(client: FlaskClient):

    r = client.post("/api/auth/register", json=valid_user_data, headers=HEADERS)
    r2 = client.post("/api/auth/register", json=valid_user_data, headers=HEADERS)

    assert r2.status_code == 400
