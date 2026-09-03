"""Register casedb ABAC endpoints through the shared commondb API adapter."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI

from gen_epix.casedb.domain import enum
from gen_epix.commondb.api.abac import (
    create_abac_endpoints as create_common_abac_endpoints,
)
from gen_epix.fastapp import App


def create_abac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **_kwargs: Any,
) -> None:
    """Register the shared ABAC endpoints for the casedb ABAC service."""
    create_common_abac_endpoints(
        router=router,
        app=app,
        service_type=enum.ServiceType.ABAC,
        handle_exception=handle_exception,
    )
