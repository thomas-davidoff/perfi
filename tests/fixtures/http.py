import pytest
from httpx import AsyncClient, ASGITransport
from app.services import AuthService


@pytest.fixture
async def authenticated_client(async_client, user) -> AsyncClient:
    """Create authenticated client with valid JWT token"""

    token, _ = AuthService.create_access_token_for_user(user_id=user.uuid)
    headers = {"Authorization": f"Bearer {token}"}

    async_client.headers.update(headers)
    return async_client


@pytest.fixture
def get_session_override(session):
    """Return a dependency that overrides the get_session dependency in FastAPI."""

    async def _override_get_session():
        yield session

    return _override_get_session


@pytest.fixture
def app(get_session_override):
    from app.main import app
    from db.session_manager import get_session

    app.dependency_overrides[get_session] = get_session_override

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(session, app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
