import os
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class UpdateResponseHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        general_headers: dict[str, str] | None = None,
        exception_headers: tuple[set[str], dict[str, str]] | None = None,
    ):
        super().__init__(app)
        self._general_headers = general_headers or {}
        self._exception_headers = exception_headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        if not self._exception_headers:
            if self._general_headers:
                response.headers.update(self._general_headers)
            response.headers.update(self._general_headers)
            return response
        for endpoints, headers in self._exception_headers:
            if request["path"] in endpoints:
                response = await call_next(request)
                response.headers.update(headers)
                return response
        response.headers.update(self._general_headers)
        app_version = os.environ.get("APP_VERSION")
        if app_version:
            content_type = response.headers.get("content-type")
            if content_type:
                content_type = content_type + ";version=" + app_version
                response.headers.update({"content-type": content_type})
        return response
