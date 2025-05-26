import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from gen_epix.fastapp.app import App
from gen_epix.fastapp.exc import AuthException


class HandleAuthExceptionMiddleware(BaseHTTPMiddleware):
    def __init__(
        # Mandatory parameters put as kwargs to comply with the signature of
        # BaseHTTPMiddleware
        self,
        app: FastAPI,
        fast_app: App = None,  # type: ignore[assignment]
        logger: logging.Logger | None = None,
    ):
        super().__init__(app)
        self._fast_app = fast_app
        self._logger = logger or fast_app.logger

    def _log_exception(self, exception: Exception) -> None:
        if self._logger:
            self._logger.warning(
                self._fast_app.create_log_message(
                    "e4cf7b23", None, exception=exception  # type: ignore[arg-type]
                ),
            )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response: Response = await call_next(request)
            return response
        except* AuthException as exception_group:
            # above except* notation is supported since python 3.11
            if self._logger:
                for exception in exception_group.exceptions:
                    self._log_exception(exception)
        # TODO: check if other domain exceptions need to be caught here
        return JSONResponse(None, status_code=401)
