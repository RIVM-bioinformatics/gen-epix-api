from collections.abc import Callable
from typing import Any, NotRequired, TypedDict


class RouterData(TypedDict):
    name: str
    create_endpoints_fn: Callable[..., Any]
    endpoints_function_kwargs: NotRequired[dict[str, Any]]
