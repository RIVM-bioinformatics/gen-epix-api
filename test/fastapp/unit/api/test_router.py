"""Unit tests for RouterData type."""

from __future__ import annotations

from gen_epix.fastapp.api.router import RouterData


class TestRouterData:
    """Tests for RouterData TypedDict."""

    def test_creates_with_required_fields(self) -> None:
        """Verify RouterData creates with required name and create_endpoints_fn."""

        def dummy_fn() -> None:
            pass

        router_data: RouterData = {
            "name": "test_router",
            "create_endpoints_fn": dummy_fn,
        }
        assert router_data["name"] == "test_router"
        assert router_data["create_endpoints_fn"] == dummy_fn

    def test_creates_with_optional_kwargs(self) -> None:
        """Verify RouterData accepts optional endpoints_function_kwargs."""

        def dummy_fn() -> None:
            pass

        kwargs = {"key1": "value1", "key2": 42}
        router_data: RouterData = {
            "name": "test_router",
            "create_endpoints_fn": dummy_fn,
            "endpoints_function_kwargs": kwargs,
        }
        assert router_data["endpoints_function_kwargs"] == kwargs

    def test_can_be_accessed_like_dict(self) -> None:
        """Verify RouterData behaves like a standard dictionary."""

        def dummy_fn() -> None:
            pass

        router_data: RouterData = {"name": "test", "create_endpoints_fn": dummy_fn}
        # Access by key
        assert "name" in router_data
        assert router_data["name"] == "test"
        # Get method
        assert router_data.get("name") == "test"
        assert router_data.get("nonexistent") is None

    def test_function_can_be_called(self) -> None:
        """Verify stored function in RouterData can be called."""
        call_count = 0

        def test_fn() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        router_data: RouterData = {"name": "test", "create_endpoints_fn": test_fn}
        result = router_data["create_endpoints_fn"]()
        assert call_count == 1
        assert result == "success"

    def test_function_with_kwargs(self) -> None:
        """Verify stored function can receive kwargs from endpoints_function_kwargs."""

        def setup_router(prefix: str, tags: list[str] | None = None) -> str:
            return f"{prefix}_{len(tags or [])}"

        router_data: RouterData = {
            "name": "test",
            "create_endpoints_fn": setup_router,
            "endpoints_function_kwargs": {"prefix": "api", "tags": ["users", "admin"]},
        }

        fn = router_data["create_endpoints_fn"]
        kwargs = router_data.get("endpoints_function_kwargs", {})
        result = fn(**kwargs)
        assert result == "api_2"
