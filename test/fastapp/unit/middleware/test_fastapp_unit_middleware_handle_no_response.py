"""Verify optional dependency handling for no-response middleware."""

import logging
from test.util.mock_compat import Mock

from gen_epix.fastapp.middleware.handle_no_response import (
    HandleNoResponseMiddleware,
)


def test_middleware_without_fast_app_uses_module_logger() -> None:
    """Allow the declared optional dependencies to be omitted."""
    middleware = HandleNoResponseMiddleware(app=Mock())

    assert middleware._logger is logging.getLogger(
        "gen_epix.fastapp.middleware.handle_no_response"
    )
