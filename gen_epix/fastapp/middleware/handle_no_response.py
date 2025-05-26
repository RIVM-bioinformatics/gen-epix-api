import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from gen_epix.fastapp.app import App


class HandleNoResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle cases where no response is returned from the endpoint.
    This is a workaround for a known issue in FastAPI where a RuntimeError is raised
    when the request is disconnected before a response is returned.

    Reference: https://stackoverflow.com/questions/71222144/runtimeerror-no-response-returned-in-fastapi-when-refresh-request
    """

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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response: Response = await call_next(request)
            return response
        except RuntimeError as exc:
            if str(exc) == "No response returned." and await request.is_disconnected():
                return JSONResponse(None, status_code=204)
            raise
