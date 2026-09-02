"""Types for application router registration."""

from collections.abc import Callable
from typing import Any, NotRequired, TypedDict


class RouterData(TypedDict):
    """Encapsulates describing a router factory registered by an application."""

    name: str
    create_endpoints_fn: Callable[..., Any]
    endpoints_function_kwargs: NotRequired[dict[str, Any]]
