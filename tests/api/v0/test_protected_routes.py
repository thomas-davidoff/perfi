import pytest
from fastapi import status
from fastapi.routing import APIRoute
from app.api.v0 import router
from httpx import AsyncClient


class TestProtectedRoutes:
    """Test that all routes except those in the whitelist require authorization."""

    UNPROTECTED_ROUTES = [
        ("/v0/auth/register", ["POST"]),
        ("/v0/auth/token", ["POST"]),
        ("/v0/auth/refresh", ["POST"]),
    ]

    def _get_route_info(self, route):
        """Extract path and methods from a route object."""
        if hasattr(route, "path") and hasattr(route, "methods"):
            return route.path, route.methods
        return None, None

    def _should_test_route(self, path: str, method: str) -> bool:
        """Determine if a route should be tested for authorization."""
        for unprotected_path, unprotected_methods in self.UNPROTECTED_ROUTES:
            if path == unprotected_path and method in unprotected_methods:
                return False

        return True

    async def test_all_protected_routes_return_401_without_authorization(
        self, async_client: AsyncClient
    ):
        """Test that all protected routes return 401 without authorization."""

        tested_routes = []
        failed_routes = []

        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue

            path, methods = self._get_route_info(route)
            if not path or not methods:
                continue

            for method in methods:
                if not self._should_test_route(path, method):
                    continue

                try:
                    response = await async_client.request(method, path)
                    tested_routes.append((method, path, response.status_code))

                    if response.status_code != status.HTTP_401_UNAUTHORIZED:
                        failed_routes.append((method, path, response.status_code))
                except Exception as e:
                    print(f"Error testing {method} {path}: {str(e)}")

        print(f"\nTested {len(tested_routes)} route/method combinations")
        if failed_routes:
            print(f"\n{len(failed_routes)} routes did not return 401:")
            for method, path, status_code in failed_routes:
                print(f"  {method} {path} -> {status_code}")

        assert (
            not failed_routes
        ), f"Found {len(failed_routes)} routes that don't require authorization"

    async def test_unprotected_routes_explicit(self, async_client: AsyncClient):
        """Explicitly test that unprotected routes work without authorization."""

        unprotected_results = []

        for path, methods in self.UNPROTECTED_ROUTES:
            for method in methods:
                response = await async_client.request(method, path)
                unprotected_results.append((method, path, response.status_code))

                assert (
                    response.status_code != status.HTTP_401_UNAUTHORIZED
                ), f"{method} {path} unexpectedly requires authorization"

            assert response.status_code != status.HTTP_404_NOT_FOUND

        print(f"\nVerified {len(unprotected_results)} unprotected routes:")
        for method, path, status_code in unprotected_results:
            print(f"  {method} {path} -> {status_code}")

    @pytest.mark.parametrize("path,methods", UNPROTECTED_ROUTES)
    async def test_unprotected_routes_parameterized(
        self, async_client: AsyncClient, path: str, methods: list[str]
    ):
        """Parameterized test for each unprotected route."""
        for method in methods:
            response = await async_client.request(method, path)
            assert (
                response.status_code != status.HTTP_401_UNAUTHORIZED
            ), f"{method} {path} should not require authorization"

    async def test_print_all_routes_for_inspection(self, async_client: AsyncClient):
        """Helper test to print all routes for manual inspection."""

        print("\nAll routes in the application:")
        print("-" * 50)

        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue

            path, methods = self._get_route_info(route)
            if not path or not methods:
                continue

            for method in methods:
                protected = (
                    "Protected"
                    if self._should_test_route(path, method)
                    else "Unprotected"
                )
                print(f"{method:6} {path:30} - {protected}")

        print("-" * 50)
        print(
            f"Total routes with methods: {sum(len(r.methods) for r in router.routes if isinstance(r, APIRoute))}"
        )
