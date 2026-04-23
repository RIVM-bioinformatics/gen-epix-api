import logging
import os
from collections.abc import Callable
from typing import Any, NoReturn

from dynaconf import Dynaconf
from fastapi import FastAPI, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from gen_epix.commondb.api.exc import generate_handle_exception_function
from gen_epix.commondb.api.router import create_routers
from gen_epix.fastapp import App
from gen_epix.fastapp.api.openapi import create_custom_openapi_function
from gen_epix.fastapp.middleware import limiter
from gen_epix.fastapp.middleware.handle_auth_exception import (
    HandleAuthExceptionMiddleware,
)
from gen_epix.fastapp.middleware.update_response_header import (
    UpdateResponseHeaderMiddleware,
)


def create_fast_api(
    app: App,
    create_routers_fn: Callable = create_routers,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    setup_logger: logging.Logger | None = None,
    api_logger: logging.Logger | None = None,
    debug: bool = False,
    **kwargs: Any,
) -> FastAPI:

    cfg: dict | Dynaconf = app.cfg

    # Set up lifespan
    @asynccontextmanager
    async def lifespan(fast_api: FastAPI) -> Any:
        if setup_logger:
            setup_logger.info(
                app.create_log_message(
                    "a49dedfc",
                    {"status": "STARTED_APP"},  # type: ignore[arg-type]
                )
            )
        yield
        if setup_logger:
            setup_logger.info(
                app.create_log_message(
                    "dcabb0ac",
                    {"status": "STOPPING_APP"},  # type: ignore[arg-type]
                )
            )

    # Initialize fast_api
    fast_api = FastAPI(
        separate_input_output_schemas=False,
        swagger_ui_init_oauth={"usePkceWithAuthorizationCodeGrant": True},
        openapi_tags=kwargs.get(
            "openapi_tags",
            [
                {
                    "name": "core",
                    "description": "Core functionality",
                }
            ],
        ),
        lifespan=lifespan,
    )

    # Add middleware
    # TODO: make this a feature flag rather than environment variable
    ratelimit_enabled = os.environ.get("RATELIMIT_ENABLED", "1") not in ("0", "false", "False")
    if not debug and ratelimit_enabled:
        # Rate limiting
        fast_api.state.limiter = limiter.limiter
        fast_api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
        # The SlowAPIMiddleware is added to fast_api globally to limit the number of requests
        # The limiter can be applied to specific routes by adding the decorator @limiter.limit
        fast_api.add_middleware(SlowAPIMiddleware)

        # GZip compression
        fast_api.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

    # Response header handling
    if not debug:
        exception_headers: list[tuple[set[str], dict[str, str]]] = [
            (
                {"/docs/oauth2-redirect"},
                dict(cfg["api"]["http_header"]["auth"]),
            ),
            (
                {"/docs", "/redoc"},
                dict(cfg["api"]["http_header"]["openapi"]),
            ),
        ]
        fast_api.add_middleware(
            UpdateResponseHeaderMiddleware,
            general_headers=dict(cfg["api"]["http_header"]["general"]),
            exception_headers=exception_headers,
        )
    # Handling of authentication exceptions
    if not debug:
        fast_api.add_middleware(
            HandleAuthExceptionMiddleware,
            fast_app=app,
            logger=api_logger,
        )

    # Add routers
    app_handle_exception = handle_exception or generate_handle_exception_function(
        app=app, logger=api_logger
    )
    routers = create_routers_fn(
        app=app,
        handle_exception=app_handle_exception,
    )
    for router in routers:
        fast_api.include_router(router, prefix=cfg["api"]["route"]["v1"])

    # Redirect root to default route
    @fast_api.get("/")
    async def redirect() -> Response:
        response = RedirectResponse(url=cfg["api"]["default_route"])
        return response

    # Update OpenAPI schema generator function
    if kwargs.pop("update_openapi_schema", False):
        update_openapi_kwargs = kwargs.pop("update_openapi_kwargs", {})
        get_open_api_kwargs = update_openapi_kwargs.pop("get_openapi_kwargs", {})
        get_open_api_kwargs.update({"routes": fast_api.routes})
        custom_openapi_fn = create_custom_openapi_function(
            get_open_api_kwargs,
            fix_schema=update_openapi_kwargs.get("fix_schema", False),
            auth_service=update_openapi_kwargs.get("auth_service"),
        )
        setattr(fast_api, "openapi", custom_openapi_fn)

    return fast_api
