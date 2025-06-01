from ast import mod
from httpx import AsyncClient
import pytest
from fastapi import status
from app.api.v0 import auth
from app.api.v0.schemas.account import (
    ApiSingleAccountResponse,
    ApiAccountFullResponse,
    ApiAccountCreateRequest,
)
from app.models import account
from app.models.account import AccountType


class TestAccountRoutes:

    class TestCreateAccount:

        endpoint = "/v0/accounts"
        method = "POST"

        @pytest.fixture(scope="class")
        async def account_data(self):
            return ApiAccountCreateRequest(
                name="some account name",
                account_type=AccountType.CASH.value,
            )

        async def test_success_returns_http_201(
            self,
            authenticated_client: AsyncClient,
            account_data: ApiAccountCreateRequest,
        ):
            r = await authenticated_client.request(
                method=self.method,
                url=self.endpoint,
                json=account_data.model_dump(mode="json"),
            )
            assert r.status_code == status.HTTP_201_CREATED

        async def test_failure_missing_data_returns_https_422(
            self,
            authenticated_client: AsyncClient,
            account_data: ApiAccountCreateRequest,
        ):
            copy = account_data.model_copy()

            for key in copy.model_dump(exclude_none=True, exclude_defaults=True):
                r = await authenticated_client.request(
                    method=self.method,
                    url=self.endpoint,
                    json={
                        k: v
                        for k, v in account_data.model_dump(mode="json").items()
                        if k != key
                    },
                )

                assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        async def test_success_returns_wrapped_full_response(
            self,
            authenticated_client: AsyncClient,
            account_data: ApiAccountCreateRequest,
        ):
            # test that a successful GET returns a ApiAccountFullResponse wrapped by
            # standard API response
            r = await authenticated_client.request(
                method=self.method,
                url=self.endpoint,
                json=account_data.model_dump(mode="json"),
            )
            ApiSingleAccountResponse.model_validate(r.json())
            ApiAccountFullResponse.model_validate(r.json()["data"])

    class TestGetAccount:
        pass

    class TestListAccounts:
        pass

    class TestUpdateAccount:
        pass

    class TestDeleteAccount:
        pass
