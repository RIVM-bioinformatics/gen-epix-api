"""Test commondb router composition requirements."""

import pytest

from gen_epix.commondb.api.router import create_routers


def test_create_routers_rejects_missing_application() -> None:
    """Reject explicit None with a clear error before endpoint registration."""
    with pytest.raises(ValueError, match="app is required"):
        create_routers(None)  # type: ignore[arg-type]
