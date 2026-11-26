"""Test background processing of upload jobs."""

import datetime
import threading
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path
from test.util.mock_compat import Mock
from typing import Any

import pytest
import sqlalchemy as sa
from pydantic import BaseModel

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.repositories import sa_model
from gen_epix.commondb.repositories.sa_mapper import CommondbSAMapperFactory
from gen_epix.commondb.repositories.system_dict import SystemDictRepository
from gen_epix.commondb.repositories.system_sa import SystemSARepository
from gen_epix.commondb.services.system import SystemService
from gen_epix.commondb.services.upload_job import (
    INTERRUPTED_JOB_DETAIL,
    UploadJobRunner,
    describe_job_failure,
)
from gen_epix.fastapp import CrudOperation, EventTiming, exc

_WAIT_SECONDS = 10


class _UploadCommand(command.Command):
    """Stand-in for an upload command."""


class _UploadResult(BaseModel):
    """Stand-in for an upload result."""

    n_created: int


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _user() -> model.User:
    return model.User.model_construct(id=uuid.uuid4())


@pytest.fixture(name="repository", params=["dict", "sqlite"])
def system_repository(
    request: pytest.FixtureRequest, tmp_path: Path
) -> Iterator[SystemDictRepository | SystemSARepository]:
    """Provide an empty system repository on each storage backend."""
    if request.param == "dict":
        yield SystemDictRepository([model.UploadJob.ENTITY], {}, missing_data="ignore")
        return
    # File-based so that worker threads, which use their own connections, see the
    # same database
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'main.db'}")
    system_db = tmp_path / "system.db"

    @sa.event.listens_for(engine, "connect")
    def _attach_system_schema(dbapi_connection: Any, _record: Any) -> None:
        dbapi_connection.execute(f"ATTACH DATABASE '{system_db}' AS system")

    sa_model.UploadJob.__table__.create(engine)
    try:
        yield SystemSARepository(
            engine,
            entities=[model.UploadJob.ENTITY],
            sa_mapper_factory=CommondbSAMapperFactory(),
        )
    finally:
        engine.dispose()


def _make_runner(
    repository: Any, handle: Callable[[Any], Any], **kwargs: Any
) -> UploadJobRunner:
    app = Mock()
    app.handle.side_effect = handle
    app.create_log_message.return_value = "log message"
    return UploadJobRunner(
        app=app,
        repository=repository,
        generate_id=uuid.uuid4,
        generate_timestamp=_now,
        logger=Mock(),
        **({"heartbeat_seconds": 3600} | kwargs),
    )


def _wait_until_finished(runner: UploadJobRunner, job_id: uuid.UUID) -> model.UploadJob:
    deadline = _now() + datetime.timedelta(seconds=_WAIT_SECONDS)
    while _now() < deadline:
        job = runner.read(job_id)
        if job.is_finished:
            return job
        threading.Event().wait(0.01)
    raise AssertionError(f"Job {job_id} did not finish")


def test_job_is_processed_in_the_background(repository: Any) -> None:
    """Return a queued job at once and store the result when the upload finishes."""
    release = threading.Event()
    handled_in: list[threading.Thread] = []

    def handle(cmd: Any) -> _UploadResult:
        handled_in.append(threading.current_thread())
        assert release.wait(_WAIT_SECONDS)
        return _UploadResult(n_created=3)

    runner = _make_runner(repository, handle)
    user_id = uuid.uuid4()
    upload_command = _UploadCommand()
    try:
        job = runner.submit(user_id, upload_command)

        assert job.status == enum.UploadJobStatus.QUEUED
        assert job.user_id == user_id
        assert job.job_type == "_UploadCommand"
        assert job.worker_id == runner.worker_id
        assert not runner.read(job.id).is_finished
        release.set()
        job = _wait_until_finished(runner, job.id)
    finally:
        runner.shutdown()

    assert job.status == enum.UploadJobStatus.SUCCEEDED
    assert job.get_result() == {"n_created": 3}
    assert job.started_at is not None and job.finished_at is not None
    assert handled_in and handled_in[0] is not threading.current_thread()
    runner.app.handle.assert_called_once_with(upload_command)
    assert runner.active_job_ids == frozenset()


@pytest.mark.parametrize(
    ("exception", "status_code", "detail"),
    [
        pytest.param(
            exc.UnauthorizedAuthError("00000001"), 403, "Access denied", id="auth"
        ),
        pytest.param(
            exc.InvalidArgumentsError("00000002", "Case 3 has no case type"),
            422,
            "Case 3 has no case type",
            id="data",
        ),
        pytest.param(
            exc.ConcurrentModificationError("00000003"),
            409,
            "System unavailable",
            id="service",
        ),
        pytest.param(RuntimeError("secret"), 500, "Internal server error", id="other"),
    ],
)
def test_failed_upload_is_stored_on_the_job(
    repository: Any, exception: Exception, status_code: int, detail: str
) -> None:
    """Store the status code and detail the synchronous endpoint would return."""

    def handle(cmd: Any) -> Any:
        raise exception

    runner = _make_runner(repository, handle)
    try:
        job = _wait_until_finished(
            runner, runner.submit(uuid.uuid4(), _UploadCommand()).id
        )
    finally:
        runner.shutdown()

    assert job.status == enum.UploadJobStatus.FAILED
    assert job.error_status_code == status_code
    assert job.error_detail == detail
    assert job.result_json is None


def test_remote_service_error_detail_is_not_exposed() -> None:
    """Hide the details of a failed call to another app, as the API does."""
    try:
        try:
            raise exc.RemoteServiceError("00000004", "seqdb said: secret")
        except exc.RemoteServiceError as cause:
            raise exc.InvalidArgumentsError("00000005", "wrapped") from cause
    except exc.InvalidArgumentsError as exception:
        assert describe_job_failure(exception) == (500, "System unavailable")


def test_submission_is_rejected_when_too_many_jobs_are_active(
    repository: Any,
) -> None:
    """Reject new jobs with 503 instead of queueing without bound."""
    release = threading.Event()
    runner = _make_runner(
        repository,
        lambda cmd: release.wait(_WAIT_SECONDS),
        max_workers=1,
        max_active=2,
    )
    try:
        runner.submit(uuid.uuid4(), _UploadCommand())
        runner.submit(uuid.uuid4(), _UploadCommand())
        with pytest.raises(exc.ServiceUnavailableError):
            runner.submit(uuid.uuid4(), _UploadCommand())
    finally:
        release.set()
        runner.shutdown()


def _store_job(repository: Any, **fields: Any) -> model.UploadJob:
    job = model.UploadJob(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        job_type="_UploadCommand",
        submitted_at=_now(),
        **fields,
    )
    with repository.uow() as uow:
        return repository.crud(
            uow, None, model.UploadJob, CrudOperation.CREATE_ONE, objs=job
        )


def test_job_of_a_stopped_worker_is_reported_as_failed(repository: Any) -> None:
    """Report an unfinished job without recent heartbeat as interrupted."""
    runner = _make_runner(repository, lambda cmd: None, stale_seconds=60)
    stale_job = _store_job(
        repository,
        status=enum.UploadJobStatus.RUNNING,
        worker_id="other-pod:1:abc",
        heartbeat_at=_now() - datetime.timedelta(seconds=120),
    )
    live_job = _store_job(
        repository,
        status=enum.UploadJobStatus.RUNNING,
        worker_id="other-pod:1:abc",
        heartbeat_at=_now() - datetime.timedelta(seconds=10),
    )

    stale_job = runner.read(stale_job.id)
    live_job = runner.read(live_job.id)

    assert stale_job.status == enum.UploadJobStatus.FAILED
    assert stale_job.error_status_code == 503
    assert stale_job.error_detail == INTERRUPTED_JOB_DETAIL
    assert live_job.status == enum.UploadJobStatus.RUNNING
    with repository.uow() as uow:
        stored = repository.crud(
            uow, None, model.UploadJob, CrudOperation.READ_ONE, obj_ids=stale_job.id
        )
    assert stored.status == enum.UploadJobStatus.FAILED


def test_heartbeat_does_not_overwrite_a_finished_job(repository: Any) -> None:
    """Leave the final status of a job alone when a heartbeat races with it."""
    runner = _make_runner(repository, lambda cmd: None)
    job = _store_job(
        repository,
        status=enum.UploadJobStatus.SUCCEEDED,
        worker_id=runner.worker_id,
        result_json="{}",
    )

    runner._update(job.id, None, heartbeat_at=_now(), only_if_unfinished=True)

    assert runner.read(job.id).status == enum.UploadJobStatus.SUCCEEDED


def test_heartbeat_refreshes_active_jobs(repository: Any) -> None:
    """Refresh the heartbeat of running jobs so other replicas see them as alive."""
    release = threading.Event()
    runner = _make_runner(
        repository, lambda cmd: release.wait(_WAIT_SECONDS), heartbeat_seconds=0.05
    )
    try:
        job = runner.submit(uuid.uuid4(), _UploadCommand())
        first_heartbeat = job.heartbeat_at
        deadline = _now() + datetime.timedelta(seconds=_WAIT_SECONDS)
        while runner.read(job.id).heartbeat_at == first_heartbeat:
            assert _now() < deadline
            threading.Event().wait(0.01)
    finally:
        release.set()
        runner.shutdown()


# System service


def _make_service(repository: Any) -> SystemService:
    service = object.__new__(SystemService)
    app = Mock()
    service._app = app
    service.upload_job_runner = Mock()
    return service


def test_submit_authorizes_the_upload_command_before_queueing() -> None:
    """Apply the upload command's BEFORE policies for the user before queueing."""
    service = _make_service(None)
    user = _user()
    upload_command = _UploadCommand(user=user)

    service.submit_upload_job(
        command.SubmitUploadJobCommand(user=user, upload_command=upload_command)
    )

    service.app.pdp.apply.assert_called_once_with(upload_command, EventTiming.BEFORE)
    service.upload_job_runner.submit.assert_called_once_with(user.id, upload_command)


def test_submit_does_not_queue_an_unauthorized_upload() -> None:
    """Reject the job at once when the user may not execute the upload."""
    service = _make_service(None)
    service.app.pdp.apply.side_effect = exc.UnauthorizedAuthError("00000006")
    user = _user()

    with pytest.raises(exc.UnauthorizedAuthError):
        service.submit_upload_job(
            command.SubmitUploadJobCommand(
                user=user, upload_command=_UploadCommand(user=user)
            )
        )

    service.upload_job_runner.submit.assert_not_called()


def test_submit_rejects_an_upload_command_of_another_user() -> None:
    """Never run an upload on behalf of a user other than the submitter."""
    service = _make_service(None)

    with pytest.raises(exc.UnauthorizedAuthError):
        service.submit_upload_job(
            command.SubmitUploadJobCommand(
                user=_user(), upload_command=_UploadCommand(user=_user())
            )
        )

    service.upload_job_runner.submit.assert_not_called()


def test_submit_sets_the_submitter_on_an_upload_command_without_user() -> None:
    """Issue an upload command without user as the submitting user."""
    service = _make_service(None)
    user = _user()
    upload_command = _UploadCommand()

    service.submit_upload_job(
        command.SubmitUploadJobCommand(user=user, upload_command=upload_command)
    )

    assert upload_command.user is user


@pytest.mark.parametrize(
    ("owner_is_requester", "job_type", "is_found"),
    [
        pytest.param(True, None, True, id="own-job"),
        pytest.param(True, "_UploadCommand", True, id="own-job-of-type"),
        pytest.param(True, "UploadSamplesCommand", False, id="other-type"),
        pytest.param(False, None, False, id="other-user"),
    ],
)
def test_retrieve_only_returns_own_jobs_of_the_requested_type(
    owner_is_requester: bool, job_type: str | None, is_found: bool
) -> None:
    """Report jobs of other users or types as non-existent."""
    service = _make_service(None)
    user = _user()
    job = model.UploadJob(
        id=uuid.uuid4(),
        user_id=user.id if owner_is_requester else uuid.uuid4(),
        job_type="_UploadCommand",
        status=enum.UploadJobStatus.RUNNING,
        submitted_at=_now(),
    )
    service.upload_job_runner.read.return_value = job
    cmd = command.RetrieveUploadJobCommand(user=user, job_id=job.id, job_type=job_type)

    if is_found:
        assert service.retrieve_upload_job(cmd) is job
    else:
        with pytest.raises(exc.InvalidIdsError):
            service.retrieve_upload_job(cmd)


def test_retrieve_reports_a_missing_job_as_invalid_id(repository: Any) -> None:
    """Translate a missing job into an invalid-ID error."""
    service = _make_service(None)
    service.upload_job_runner = _make_runner(repository, lambda cmd: None)

    with pytest.raises(exc.InvalidIdsError):
        service.retrieve_upload_job(
            command.RetrieveUploadJobCommand(user=_user(), job_id=uuid.uuid4())
        )
