"""Verify FastAPI setup preserves caller-owned OpenAPI options."""

from test.util.mock_compat import Mock

from gen_epix.commondb import app_setup


def test_create_fast_api_does_not_mutate_openapi_kwargs(monkeypatch) -> None:
    """Keep both caller-owned OpenAPI mappings unchanged during setup."""
    captured_openapi_kwargs = {}

    def create_custom_openapi_function(get_open_api_kwargs, **kwargs):
        captured_openapi_kwargs.update(get_open_api_kwargs)
        return lambda: {}

    monkeypatch.setattr(
        app_setup, "create_custom_openapi_function", create_custom_openapi_function
    )
    nested_kwargs = {"title": "Test API"}
    update_kwargs = {"get_openapi_kwargs": nested_kwargs, "fix_schema": False}
    app = Mock(cfg={"api": {"default_route": "/v1", "route": {"v1": "/v1"}}})

    app_setup.create_fast_api(
        app=app,
        create_routers_fn=lambda **kwargs: [],
        handle_exception=Mock(),
        debug=True,
        update_openapi_schema=True,
        update_openapi_kwargs=update_kwargs,
    )

    assert update_kwargs == {
        "get_openapi_kwargs": {"title": "Test API"},
        "fix_schema": False,
    }
    assert nested_kwargs == {"title": "Test API"}
    assert "routes" in captured_openapi_kwargs
