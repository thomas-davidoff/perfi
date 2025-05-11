from uuid import uuid4
import pytest
from fastapi import status
from decimal import Decimal
from datetime import date
from tests.utils import faker
from httpx import AsyncClient
from app.api.v0.schemas.transaction import (
    ApiSingletransactionResponse,
    ApiTransactionCreateRequest,
)


class TestTransactionRoutes:

    @pytest.fixture
    async def transaction_data(self, account, expense_category):
        """Create valid transaction data for testing"""
        return ApiTransactionCreateRequest(
            account_id=account.uuid,
            category_id=expense_category.uuid,
            amount=Decimal("-50.25"),
            description=faker.sentence()[:50],
            date=date.today(),
            is_pending=False,
            notes=faker.paragraph(),
        )

    class TestCreateTransaction:
        async def test_success_returns_201_created_status_code(
            self,
            authenticated_client: AsyncClient,
            transaction_data: ApiTransactionCreateRequest,
        ):
            data_dict = transaction_data.model_dump(mode="json")

            response = await authenticated_client.post(
                "/v0/transactions/", json=data_dict
            )

            assert response.status_code == status.HTTP_201_CREATED

        async def test_success_returns_valid_transaction(
            self,
            authenticated_client: AsyncClient,
            transaction_data: ApiTransactionCreateRequest,
        ):
            data_dict = transaction_data.model_dump(mode="json")
            response = await authenticated_client.post(
                "/v0/transactions/", json=data_dict
            )

            ApiSingletransactionResponse.model_validate(response.json())

        async def test_missing_data_returns_422_status_code(
            self,
            authenticated_client: AsyncClient,
            transaction_data: ApiTransactionCreateRequest,
        ):
            data_dict = transaction_data.model_dump(mode="json")
            data_dict.pop("account_id")

            response = await authenticated_client.post(
                "/v0/transactions/", json=data_dict
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        async def test_invalid_account_returns_400_bad_request(
            self,
            authenticated_client: AsyncClient,
            transaction_data: ApiTransactionCreateRequest,
        ):
            data_dict = transaction_data.model_dump(mode="json")
            data_dict.update(account_id=str(uuid4()))

            response = await authenticated_client.post(
                "/v0/transactions/", json=data_dict
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    class TestListTransactions:
        endpoint = "/v0/transactions/"

        async def test_success_returns_200(self, authenticated_client: AsyncClient):
            response = await authenticated_client.get(self.endpoint)

            assert response.status_code == status.HTTP_200_OK

        async def test_success_no_transactions_returns_empty_list(
            self, authenticated_client: AsyncClient
        ):
            response = await authenticated_client.get(self.endpoint)

            assert response.json() == {"data": []}
