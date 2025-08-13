import logging
from typing import Any, Callable, NoReturn

from fastapi import FastAPI, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from gen_epix.casedb.api.router import create_routers
from gen_epix.common.api.exc import generate_handle_exception_function
from gen_epix.fastapp import App
from gen_epix.fastapp.api.openapi import create_custom_openapi_function
from gen_epix.fastapp.enum import LogLevel
from gen_epix.fastapp.middleware import (
    HandleAuthExceptionMiddleware,
    UpdateResponseHeaderMiddleware,
    limiter,
)


def create_fast_api(
    cfg: dict,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    setup_logger: logging.Logger | None = None,
    api_logger: logging.Logger | None = None,
    debug: bool = False,
    **kwargs: Any,
) -> FastAPI:

    app_id = kwargs.pop("app_id", app.generate_id())

    # Set up lifespan
    @asynccontextmanager
    async def lifespan(fast_api: FastAPI) -> Any:
        if setup_logger:
            setup_logger.info(
                app.create_log_message(
                    "a49dedfc",
                    {"status": "STARTING_APP", "app_id": str(app_id)},  # type: ignore[arg-type]
                )
            )
        yield
        if setup_logger:
            setup_logger.info(
                app.create_log_message(
                    "dcabb0ac",
                    {"status": "STOPPING_APP", "app_id": str(app_id)},  # type: ignore[arg-type]
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
    # Rate limiting
    if not debug:
        fast_api.state.limiter = limiter.limiter
        fast_api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
        # The SlowAPIMiddleware is added to fast_api globally to limit the number of requests
        # The limiter can be applied to specific routes by adding the decorator @limiter.limit
        fast_api.add_middleware(SlowAPIMiddleware)

    # Response header handling
    if not debug:
        fast_api.add_middleware(
            UpdateResponseHeaderMiddleware,
            general_headers=cfg.api.http_header.general,
            exception_headers=[
                ({"/docs/oauth2-redirect"}, cfg.api.http_header.auth),
                ({"/docs", "/redoc"}, cfg.api.http_header.openapi),
            ],
        )
    # Handling of authentication exceptions
    if not debug:
        fast_api.add_middleware(
            HandleAuthExceptionMiddleware,
            fast_app=app,
            logger=api_logger,
        )

    # Add routers
    handle_exception = generate_handle_exception_function(app=app, logger=api_logger)
    routers = create_routers(
        app=app,
        registered_user_dependency=registered_user_dependency,
        new_user_dependency=new_user_dependency,
        idp_user_dependency=idp_user_dependency,
        handle_exception=handle_exception,
    )
    for router in routers:
        fast_api.include_router(router, prefix=cfg.api.route.v1)

    # Redirect root to default route
    @fast_api.get("/")
    async def redirect() -> Response:
        response = RedirectResponse(url=cfg.api.default_route)
        return response

    # Update OpenAPI schema generator function
    if kwargs.pop("update_openapi_schema", False):
        update_openapi_kwargs = kwargs.pop("update_openapi_kwargs", {})
        get_open_api_kwargs = update_openapi_kwargs.pop("get_openapi_kwargs", {})
        get_open_api_kwargs.update({"routes": fast_api.routes})
        custom_openapi_function = create_custom_openapi_function(
            get_open_api_kwargs,
            fix_schema=update_openapi_kwargs.get("fix_schema", False),
            auth_service=update_openapi_kwargs.get("auth_service"),
        )
        setattr(fast_api, "openapi", custom_openapi_function)

    return fast_api
