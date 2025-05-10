import pytest
from fastapi import status
from decimal import Decimal
from datetime import date
from app.schemas import TransactionCreateSchema
from tests.utils import faker
from app.services import AuthService
from httpx import AsyncClient


class TestTransactionRoutes:

    @pytest.fixture
    async def authenticated_client(self, mocker, async_client, user) -> AsyncClient:
        """Create authenticated client with valid JWT token"""

        mock_auth = mocker.patch.object(
            AuthService, "authenticate_user", return_value=user
        )
        response = await async_client.post(
            "/v0/auth/token",
            data={
                "username": user.email,
                "password": "password123",
            },
        )  # This should return a serialized BearerAccessTokenRefreshTokenPair

        assert response.status_code == status.HTTP_200_OK

        async_client.headers.update(
            {"Authorization": f"Bearer {response.json()['access_token']}"}
        )
        return async_client

    @pytest.fixture
    async def transaction_data(self, account, expense_category):
        """Create valid transaction data for testing"""
        return TransactionCreateSchema(
            account_id=account.uuid,
            category_id=expense_category.uuid,
            amount=Decimal("-50.25"),
            description=faker.sentence()[:50],
            date=date.today(),
            is_pending=False,
            notes=faker.paragraph(),
        )

    class TestCreate:
        async def test_success_returns_201_created_status_code(
            self,
            authenticated_client: AsyncClient,
            transaction_data: TransactionCreateSchema,
        ):
            data_dict = transaction_data.model_dump(mode="json")

            response = await authenticated_client.post(
                "/v0/transactions/", json=data_dict
            )

            assert response.status_code == status.HTTP_201_CREATED

        async def something(self):
            pass
