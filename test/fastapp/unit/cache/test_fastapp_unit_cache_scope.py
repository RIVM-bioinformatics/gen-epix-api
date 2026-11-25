"""Verify request-local cache scope behavior."""

from gen_epix.fastapp.cache.scope import RequestScope


def test_activate_yields_the_backing_mapping() -> None:
    """Expose direct writes through the active request scope."""
    scope = RequestScope()

    with RequestScope.activate() as values:
        values["cache-key"] = "cached-value"

        assert scope.get("cache-key") == "cached-value"

    assert scope.get("cache-key") is None
