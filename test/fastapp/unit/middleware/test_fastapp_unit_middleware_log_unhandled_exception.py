"""Tests for logging unhandled exceptions as structured log items."""

from test.util.mock_compat import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from gen_epix.fastapp.middleware.log_unhandled_exception import (
    create_unhandled_exception_handler,
)


def _client(fast_app: object | None, logger: Mock) -> TestClient:
    api = FastAPI()

    @api.get("/boom")
    def boom() -> None:
        raise ValueError("Statement error: ... (1205)")

    api.add_exception_handler(
        Exception,
        create_unhandled_exception_handler(fast_app=fast_app, logger=logger),  # type: ignore[arg-type]
    )
    return TestClient(api, raise_server_exceptions=False)


def test_unhandled_exception_is_logged_as_structured_item() -> None:
    fast_app = Mock()
    fast_app.create_log_message.return_value = '{"code": "9b18f4b8"}'
    logger = Mock()

    response = _client(fast_app, logger).get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    args, kwargs = fast_app.create_log_message.call_args
    assert args == ("9b18f4b8", "UNHANDLED_EXCEPTION")
    assert kwargs["method"] == "GET"
    assert kwargs["path"] == "/boom"
    assert isinstance(kwargs["exception"], ValueError)
    logger.error.assert_called_once_with('{"code": "9b18f4b8"}')


def test_without_app_logs_plain_message_with_traceback() -> None:
    logger = Mock()

    response = _client(None, logger).get("/boom")

    assert response.status_code == 500
    logger.error.assert_called_once()
    assert isinstance(logger.error.call_args.kwargs["exc_info"], ValueError)
