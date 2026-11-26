"""Test uploads through the background job endpoints of a remote app."""

from test.util.mock_compat import Mock
from typing import Any
from uuid import uuid4

import httpx
import pytest
from pydantic import BaseModel

from gen_epix.commondb.services import client as commondb_client
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import HttpMethod
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.services.client import SeqdbClient

_ROUTE = "/upload/samples"


class _Result(BaseModel):
    """Stand-in for an upload result."""

    samples: list = []


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(commondb_client.time, "sleep", lambda _seconds: None)


def _status_error(status_code: int) -> httpx.HTTPStatusError:
    response = httpx.Response(status_code, request=httpx.Request("GET", "http://x"))
    return httpx.HTTPStatusError("error", request=response.request, response=response)


def _client(responses: list[Any], **kwargs: Any) -> tuple[SeqdbClient, Mock]:
    client = SeqdbClient(host="localhost", port=8001, **kwargs)
    request = Mock(side_effect=responses)
    client.request = request  # type: ignore[method-assign]
    return client, request


def _cmd() -> command.UploadSamplesCommand:
    return command.UploadSamplesCommand(
        sample_batch=model.SampleBatchForUpload(samples=[])
    )


def _job(status: str, **fields: Any) -> dict[str, Any]:
    return {"id": "job-1", "status": status} | fields


def test_polls_until_the_job_succeeds() -> None:
    """Poll with GET until the job is finished and parse its result."""
    client, request = _client(
        [_job("QUEUED"), _job("RUNNING"), _job("SUCCEEDED", result={"samples": []})]
    )
    cmd = _cmd()

    result = client.upload_via_job(cmd, _Result, exclude={"user"})

    assert result == _Result()
    route = client.get_route(cmd)
    assert [call.args[1] for call in request.call_args_list] == [
        HttpMethod.POST,
        HttpMethod.GET,
        HttpMethod.GET,
    ]
    assert request.call_args_list[1].kwargs["route"] == f"{route}/jobs/job-1"


def test_failed_job_raises_the_status_of_the_synchronous_upload() -> None:
    """Raise a remote error with the status the synchronous upload would return."""
    client, _ = _client(
        [_job("FAILED", error_status_code=422, error_detail="Bad sample")]
    )

    with pytest.raises(exc.RemoteServiceError) as exc_info:
        client.upload_via_job(_cmd(), _Result)

    assert exc_info.value.get_http_status_code() == 422
    assert "HTTP status 422" in str(exc_info.value.message)
    assert "Bad sample" in str(exc_info.value.message)


def test_falls_back_to_the_synchronous_endpoint_without_job_endpoints() -> None:
    """Use the synchronous endpoint, from then on, if the remote app is older."""
    client, request = _client([_status_error(404), {"samples": []}, {"samples": []}])
    cmd = _cmd()

    assert client.upload_via_job(cmd, _Result) == _Result()
    assert client.upload_via_job(cmd, _Result) == _Result()

    routes = [call.kwargs["route"] for call in request.call_args_list]
    route = client.get_route(cmd)
    assert routes == [f"{route}/jobs", route, route]
    assert client.use_upload_jobs is False


def test_uses_the_synchronous_endpoint_when_jobs_are_disabled() -> None:
    """Allow callers to opt out of upload jobs."""
    client, request = _client([{"samples": []}], use_upload_jobs=False)
    cmd = _cmd()

    client.upload_via_job(cmd, _Result)

    assert request.call_args.kwargs["route"] == client.get_route(cmd)


def test_other_submission_errors_are_raised() -> None:
    """Do not fall back on errors that the synchronous endpoint would also give."""
    client, _ = _client([_status_error(403)])

    with pytest.raises(httpx.HTTPStatusError):
        client.upload_via_job(_cmd(), _Result)


def test_transient_poll_errors_are_retried() -> None:
    """Keep polling through a restarting replica or ingress hiccup."""
    client, _ = _client(
        [
            _job("QUEUED"),
            httpx.ConnectError("refused"),
            _status_error(503),
            _job("SUCCEEDED", result={"samples": []}),
        ]
    )

    assert client.upload_via_job(_cmd(), _Result) == _Result()


def test_job_that_does_not_finish_in_time_raises() -> None:
    """Give up after the configured timeout."""
    client, _ = _client(
        [_job("QUEUED")] + [_job("RUNNING")] * 100, upload_job_timeout=1
    )

    with pytest.raises(exc.ServiceUnavailableError):
        client.upload_via_job(_cmd(), _Result)
