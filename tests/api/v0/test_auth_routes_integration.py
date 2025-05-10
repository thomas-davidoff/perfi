from fastapi import status
import pytest
from app.schemas import UserCreateSchema, UserSchema
from tests.utils import faker
from app.main import app
from pytest_mock import MockerFixture
import pydantic

from app.api import exception_handlers


class TestAuthRoutes:
    class TestRegister:
        async def test_success(self, async_client):
            user_data = UserCreateSchema(email=faker.email(), password=faker.password())
            response = await async_client.post(
                "/v0/auth/register", json=user_data.model_dump()
            )
            assert response.status_code == status.HTTP_201_CREATED

        async def test_returned_user_doesnt_include_hashed_password(self, async_client):
            user_data = UserCreateSchema(email=faker.email(), password=faker.password())
            response = await async_client.post(
                "/v0/auth/register", json=user_data.model_dump()
            )

            assert "hashed_password" not in response.json()["data"]

            with pytest.raises(
                pydantic.ValidationError,
                match="1 validation error for UserSchema\nhashed_password",
            ):
                # creating user schema from response should not contain the hashed password, but it
                # should contain everything else. Thus, 1 err should be raised with the match above.
                UserSchema(**response.json()["data"])

        async def test_raises_exception_on_duplicate(
            self, async_client, mocker: MockerFixture
        ):
            user_data = UserCreateSchema(email=faker.email(), password=faker.password())
            response = await async_client.post(
                "/v0/auth/register", json=user_data.model_dump()
            )
            assert response.status_code == status.HTTP_201_CREATED

            # with pytest.raises(Exception):
            response = await async_client.post(
                "/v0/auth/register", json=user_data.model_dump()
            )

            assert response.status_code == status.HTTP_409_CONFLICT
            assert {
                "error": f"User with email {user_data.email} already exists"
            } == response.json()


# @pytest.mark.parametrize(
#     "path",
#     ["/v0/auth/whoami"],
# )
# async def test_protected_routes(self, client: TestClient, path):
#     """Checks that each of the routes returns 401 Unauthorized when a token is not provided"""
#     response = client.get(
#         path,
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
# async def test_register_success_returns_user_schema(
#     self, mocker: MockerFixture, client: TestClient
# ):
#     user_data = UserCreateSchema(email=faker.email(), password=faker.password())
#     response = await client.post(
#         "/v0/auth/register", content=user_data.model_dump_json()
#     )

#     print(response)

#     assert response.status_code == status.HTTP_201_CREATED

# async def test_register_failure(self, client: TestClient):
#     pass

# async def test_token_failure_returns_401_unauthorized(self, client: TestClient):
#     pass

# async def test_token_success_returns_valid_token(self, client: TestClient):
#     pass

# async def test_whoami_success_returns_user_schema(self, client: TestClient):
#     pass

# async def test_whoami_failure_invalid_token(self, client: TestClient):
#     pass
