"""Exception handler that logs unhandled exceptions as structured log items."""

import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from gen_epix.fastapp.app import App


def create_unhandled_exception_handler(
    fast_app: App | None = None,
    logger: logging.Logger | None = None,
) -> Callable[[Request, Exception], Awaitable[Response]]:
    """Create a handler that logs an unhandled exception and returns HTTP 500.

    Without it, an exception that escapes every route handler and middleware is
    only written as plain text to stderr by the ASGI server, without code,
    request path or method, and does not show up in structured log queries.

    Args:
        fast_app: Application whose log item format is used.
        logger: Logger to write to; defaults to the application logger.

    Returns:
        Exception handler to register for ``Exception`` on the FastAPI app.
    """
    handler_logger = logger or (fast_app.logger if fast_app is not None else None)

    async def handle_unhandled_exception(
        request: Request, exception: Exception
    ) -> Response:
        """Log the exception with request context and return a generic 500."""
        if handler_logger:
            if fast_app is not None:
                # The log item serializes the exception including its stack trace
                handler_logger.error(
                    fast_app.create_log_message(
                        "9b18f4b8",
                        "UNHANDLED_EXCEPTION",
                        method=request.method,
                        path=request.url.path,
                        exception=exception,
                    )
                )
            else:
                handler_logger.error(
                    "Unhandled exception on %s %s",
                    request.method,
                    request.url.path,
                    exc_info=exception,
                )
        return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

    return handle_unhandled_exception
