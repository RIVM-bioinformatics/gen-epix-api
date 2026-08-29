"""Utilities for the fastapp router module."""

from collections.abc import Callable
from typing import Any, NotRequired, TypedDict


class RouterData(TypedDict):
    """Provide the router data framework abstraction."""

    name: str
    create_endpoints_fn: Callable[..., Any]
    endpoints_function_kwargs: NotRequired[dict[str, Any]]
