"""Test that remote-app errors are returned opaquely by the API exception handler."""

from test.util.mock_compat import Mock

import pytest
from fastapi import HTTPException

from gen_epix.commondb.api.exc import handle_exception
from gen_epix.fastapp.exc import RemoteServiceError, ServiceException

_REMOTE_MESSAGE = (
    "HTTP status {status} error when handling remote command X: "
    "Client error for url 'https://seqdb.internal/v1/secret'"
)


def _app() -> Mock:
    app = Mock()
    app.create_log_message.return_value = "log message"
    return app


@pytest.mark.parametrize("status", [401, 403, 404, 409, 422, 429, 500, 502, 504])
def test_remote_service_error_is_returned_as_opaque_500(status: int) -> None:
    error = RemoteServiceError(
        "b7b0a22c", _REMOTE_MESSAGE.format(status=status), {"status_code": status}
    )

    with pytest.raises(HTTPException) as e:
        handle_exception(_app(), None, "id", None, error)

    assert e.value.status_code == 500
    assert e.value.detail == "System unavailable"
    assert not e.value.headers


def test_service_exception_caused_by_remote_service_error_is_opaque() -> None:
    remote = RemoteServiceError(
        "b7b0a22c", _REMOTE_MESSAGE.format(status=401), {"status_code": 401}
    )
    wrapper = ServiceException("11111111", "wrapped", remote.http_props)
    wrapper.__cause__ = remote

    with pytest.raises(HTTPException) as e:
        handle_exception(_app(), None, "id", None, wrapper)

    assert e.value.status_code == 500
    assert e.value.detail == "System unavailable"


def test_plain_service_exception_keeps_its_own_status() -> None:
    error = ServiceException("11111111", "x", {"status_code": 409})

    with pytest.raises(HTTPException) as e:
        handle_exception(_app(), None, "id", None, error)

    assert e.value.status_code == 409
