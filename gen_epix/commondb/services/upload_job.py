"""Process upload commands in background threads and track them as upload jobs.

Uploads can take minutes. Processed inside an HTTP request they hold a request
thread and a database connection for that long and run into the ingress timeout.
The ``UploadJobRunner`` instead processes them on a small, bounded thread pool in
the same process, while the client polls the job's status.

The job row is the source of truth for the job's status, so that any replica can
answer a status request. Only the process that runs a job writes to its row,
except for a replica that reports a job as FAILED once the owning process has
stopped sending heartbeats (e.g. because its pod was restarted).

Configuration, per process, through environment variables:

- ``UPLOAD_JOB_MAX_WORKERS``: uploads processed concurrently (default 2).
- ``UPLOAD_JOB_MAX_ACTIVE``: queued plus running jobs before new submissions are
  rejected with 503 (default 20).
- ``UPLOAD_JOB_HEARTBEAT_SECONDS``: interval of the heartbeat of active jobs
  (default 30).
- ``UPLOAD_JOB_STALE_SECONDS``: age of the last heartbeat after which an
  unfinished job is reported as FAILED (default 300).
- ``UPLOAD_JOB_RETENTION_DAYS``: age after which jobs are deleted (default 7).
  Every process deletes old jobs at most once per hour.
"""

from __future__ import annotations

import datetime
import logging
import os
import socket
import threading
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from uuid import UUID

import pydantic_core

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.repository import BaseSystemRepository
from gen_epix.fastapp import App, CrudOperation, exc

DEFAULT_MAX_WORKERS = int(os.environ.get("UPLOAD_JOB_MAX_WORKERS", "2"))
DEFAULT_MAX_ACTIVE = int(os.environ.get("UPLOAD_JOB_MAX_ACTIVE", "20"))
DEFAULT_HEARTBEAT_SECONDS = float(os.environ.get("UPLOAD_JOB_HEARTBEAT_SECONDS", "30"))
DEFAULT_STALE_SECONDS = float(os.environ.get("UPLOAD_JOB_STALE_SECONDS", "300"))
DEFAULT_RETENTION_SECONDS = (
    float(os.environ.get("UPLOAD_JOB_RETENTION_DAYS", "7")) * 24 * 3600
)
CLEANUP_INTERVAL_SECONDS = 3600.0

INTERRUPTED_JOB_DETAIL = (
    "The upload job was interrupted because its worker stopped. Resubmit the upload."
)
_ERROR_DETAIL_MAX_LENGTH = 2000


def describe_job_failure(exception: BaseException) -> tuple[int, str]:
    """Return the HTTP status code and detail the synchronous endpoint would return.

    Mirrors the API exception handler: details of service and remote errors are not
    exposed, while messages of data errors are, since they describe the upload.

    Args:
        exception: Exception raised while processing the upload command.

    Returns:
        HTTP status code and error detail.
    """
    current: BaseException | None = exception
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        if isinstance(current, exc.RemoteServiceError):
            return 500, "System unavailable"
        seen.add(id(current))
        current = current.__cause__
    if isinstance(exception, exc.AuthException):
        return exception.get_http_status_code(), "Access denied"
    if isinstance(exception, exc.ServiceException):
        return exception.get_http_status_code(), "System unavailable"
    if isinstance(exception, exc.IdsError):
        status_code = (
            409
            if isinstance(
                exception, (exc.LinkConstraintViolationError, exc.DuplicateIdsError)
            )
            else 422
        )
        return status_code, str(exception.message or "Invalid ids provided")
    if isinstance(exception, exc.DomainException):
        return 422, str(exception.message or exception)
    return 500, "Internal server error"


def _as_utc(value: datetime.datetime) -> datetime.datetime:
    """Return the value as an aware UTC date-time; naive values are taken as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.UTC)
    return value.astimezone(datetime.UTC)


class UploadJobRunner:
    """Encapsulates the background processing of upload jobs in one process.

    Upload commands are dispatched through ``App.handle`` on a worker thread. Since
    the command stack is thread-local, the upload command is an initial command
    there and all its policies are applied, as for a synchronous request.
    """

    def __init__(
        self,
        app: App,
        repository: BaseSystemRepository,
        generate_id: Callable[[], Any],
        generate_timestamp: Callable[[], datetime.datetime],
        logger: logging.Logger | None = None,
        max_workers: int = DEFAULT_MAX_WORKERS,
        max_active: int = DEFAULT_MAX_ACTIVE,
        heartbeat_seconds: float = DEFAULT_HEARTBEAT_SECONDS,
        stale_seconds: float = DEFAULT_STALE_SECONDS,
        retention_seconds: float = DEFAULT_RETENTION_SECONDS,
    ) -> None:
        """Initialize the runner; threads are started on the first submission.

        Args:
            app: Application that dispatches the upload commands.
            repository: System repository that stores the job rows.
            generate_id: Factory for job IDs.
            generate_timestamp: Factory for the current UTC date-time.
            logger: Optional logger for job failures.
            max_workers: Number of uploads processed concurrently.
            max_active: Number of queued plus running jobs accepted.
            heartbeat_seconds: Interval of the heartbeat of active jobs.
            stale_seconds: Heartbeat age after which an unfinished job is stale.
            retention_seconds: Age after which a job is deleted.
        """
        self.app = app
        self.repository = repository
        self.generate_id = generate_id
        self.generate_timestamp = generate_timestamp
        self.logger = logger
        self.max_workers = max_workers
        self.max_active = max_active
        self.heartbeat_seconds = heartbeat_seconds
        self.stale_seconds = stale_seconds
        self.retention_seconds = retention_seconds
        self._last_cleanup_at: datetime.datetime | None = None
        self.worker_id = f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:8]}"
        self._executor: ThreadPoolExecutor | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        # Serializes read-modify-write of job rows within this process, so that a
        # heartbeat cannot overwrite a status change written at the same time
        self._lock = threading.RLock()
        self._active_job_ids: set[UUID] = set()

    @property
    def active_job_ids(self) -> frozenset[UUID]:
        """Return the IDs of the jobs queued or running in this process."""
        with self._lock:
            return frozenset(self._active_job_ids)

    def submit(self, user_id: UUID, upload_command: command.Command) -> model.UploadJob:
        """Store a new job and queue its upload command for processing.

        Args:
            user_id: ID of the submitting user.
            upload_command: Authorized upload command to process.

        Returns:
            The stored job, with status QUEUED.

        Raises:
            ServiceUnavailableError: If this process already has the maximum number
                of active jobs.
        """
        self._clean_up_if_due()
        with self._lock:
            if len(self._active_job_ids) >= self.max_active:
                raise exc.ServiceUnavailableError(
                    "c1e7a5d2",
                    "Too many upload jobs are being processed, try again later",
                )
            now = self.generate_timestamp()
            job = model.UploadJob(
                id=self.generate_id(),
                user_id=user_id,
                job_type=type(upload_command).__name__,
                status=enum.UploadJobStatus.QUEUED,
                submitted_at=now,
                heartbeat_at=now,
                worker_id=self.worker_id,
            )
            with self.repository.uow() as uow:
                job = self.repository.crud(
                    uow, user_id, model.UploadJob, CrudOperation.CREATE_ONE, objs=job
                )
            assert job.id is not None
            self._active_job_ids.add(job.id)
            self._ensure_started()
        assert self._executor is not None
        self._executor.submit(self._run, job.id, user_id, upload_command)
        return job

    def read(self, job_id: UUID) -> model.UploadJob:
        """Read a job, reporting it as FAILED if its worker has stopped.

        Args:
            job_id: ID of the job.

        Returns:
            The job.

        Raises:
            InvalidIdsError: If the job does not exist.
        """
        with self.repository.uow() as uow:
            job: model.UploadJob = self.repository.crud(
                uow, None, model.UploadJob, CrudOperation.READ_ONE, obj_ids=job_id
            )
        if self._is_stale(job):
            job = self._update(
                job_id,
                job.user_id,
                status=enum.UploadJobStatus.FAILED,
                finished_at=self.generate_timestamp(),
                error_status_code=503,
                error_detail=INTERRUPTED_JOB_DETAIL,
                only_if_unfinished=True,
            )
        return job

    def shutdown(self, wait: bool = True) -> None:
        """Stop the heartbeat and the worker threads.

        Args:
            wait: Whether to wait for running jobs to finish.
        """
        self._stop_event.set()
        if self._executor is not None:
            self._executor.shutdown(wait=wait, cancel_futures=not wait)

    def clean_up(self) -> int:
        """Delete the jobs submitted longer ago than the retention period.

        Jobs that are still active in this process are kept.

        Returns:
            The number of deleted jobs.
        """
        cutoff = _as_utc(self.generate_timestamp()) - datetime.timedelta(
            seconds=self.retention_seconds
        )
        active_job_ids = self.active_job_ids
        with self.repository.uow() as uow:
            job_ids = [
                job_id
                for job_id, submitted_at in self.repository.read_fields(
                    uow, None, model.UploadJob, ["id", "submitted_at"]
                )
                if _as_utc(submitted_at) < cutoff and job_id not in active_job_ids
            ]
            if job_ids:
                self.repository.crud(
                    uow,
                    None,
                    model.UploadJob,
                    CrudOperation.DELETE_SOME,
                    obj_ids=job_ids,
                )
        return len(job_ids)

    def _clean_up_if_due(self) -> None:
        """Delete old jobs if the last clean-up was over an interval ago."""
        now = _as_utc(self.generate_timestamp())
        with self._lock:
            if (
                self._last_cleanup_at is not None
                and (now - self._last_cleanup_at).total_seconds()
                < CLEANUP_INTERVAL_SECONDS
            ):
                return
            self._last_cleanup_at = now
        try:
            self.clean_up()
        except Exception as exception:  # pylint: disable=broad-except
            if self.logger:
                self.logger.warning(
                    self.app.create_log_message(
                        "d5a1f9c3", "UPLOAD_JOB_CLEANUP_ERROR", exception=exception
                    )
                )

    def _is_stale(self, job: model.UploadJob) -> bool:
        """Return whether an unfinished job's worker has stopped sending heartbeats."""
        if job.is_finished:
            return False
        if job.worker_id == self.worker_id and job.id in self.active_job_ids:
            return False
        if job.heartbeat_at is None:
            return True
        age = _as_utc(self.generate_timestamp()) - _as_utc(job.heartbeat_at)
        return age.total_seconds() > self.stale_seconds

    def _ensure_started(self) -> None:
        """Start the worker pool and the heartbeat thread if not running yet."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers, thread_name_prefix="upload-job"
            )
        if self._heartbeat_thread is None:
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop, name="upload-job-heartbeat", daemon=True
            )
            self._heartbeat_thread.start()

    def _run(
        self, job_id: UUID, user_id: UUID, upload_command: command.Command
    ) -> None:
        """Process one upload command and store its outcome on the job."""
        try:
            self._update(
                job_id,
                user_id,
                status=enum.UploadJobStatus.RUNNING,
                started_at=self.generate_timestamp(),
            )
            try:
                result = self.app.handle(upload_command)
            except Exception as exception:  # pylint: disable=broad-except
                status_code, detail = describe_job_failure(exception)
                if self.logger:
                    self.logger.warning(
                        self.app.create_log_message(
                            "f6b2d8e4",
                            "UPLOAD_JOB_FAILED",
                            job_id=str(job_id),
                            exception=exception,
                        )
                    )
                self._update(
                    job_id,
                    user_id,
                    status=enum.UploadJobStatus.FAILED,
                    finished_at=self.generate_timestamp(),
                    error_status_code=status_code,
                    error_detail=detail[:_ERROR_DETAIL_MAX_LENGTH],
                )
                return
            self._update(
                job_id,
                user_id,
                status=enum.UploadJobStatus.SUCCEEDED,
                finished_at=self.generate_timestamp(),
                result_json=pydantic_core.to_json(result).decode("utf-8"),
            )
        except Exception as exception:  # pylint: disable=broad-except
            # Storing the outcome failed; the job is reported as FAILED once its
            # heartbeat is stale
            if self.logger:
                self.logger.error(
                    self.app.create_log_message(
                        "a9d3e7b1",
                        "UPLOAD_JOB_ERROR",
                        job_id=str(job_id),
                        exception=exception,
                    ),
                    exc_info=True,
                )
        finally:
            with self._lock:
                self._active_job_ids.discard(job_id)

    def _heartbeat_loop(self) -> None:
        """Periodically refresh the heartbeat of the jobs active in this process."""
        while not self._stop_event.wait(self.heartbeat_seconds):
            self._clean_up_if_due()
            for job_id in self.active_job_ids:
                try:
                    self._update(
                        job_id,
                        None,
                        heartbeat_at=self.generate_timestamp(),
                        only_if_unfinished=True,
                    )
                except Exception as exception:  # pylint: disable=broad-except
                    if self.logger:
                        self.logger.warning(
                            self.app.create_log_message(
                                "b4e8c2f6",
                                "UPLOAD_JOB_HEARTBEAT_ERROR",
                                job_id=str(job_id),
                                exception=exception,
                            )
                        )

    def _update(
        self,
        job_id: UUID,
        user_id: UUID | None,
        only_if_unfinished: bool = False,
        **fields: Any,
    ) -> model.UploadJob:
        """Read, update and store a job row under the process-wide lock.

        Args:
            job_id: ID of the job.
            user_id: ID of the user recorded as modifier, if any.
            only_if_unfinished: Leave a job that already finished unchanged.
            **fields: Field values to set.

        Returns:
            The stored job.
        """
        with self._lock:
            with self.repository.uow() as uow:
                job: model.UploadJob = self.repository.crud(
                    uow,
                    user_id,
                    model.UploadJob,
                    CrudOperation.READ_ONE,
                    obj_ids=job_id,
                )
                if only_if_unfinished and job.is_finished:
                    return job
                if "status" in fields or "heartbeat_at" not in fields:
                    fields.setdefault("heartbeat_at", self.generate_timestamp())
                updated_job = job.model_copy(update=fields)
                return self.repository.crud(  # type: ignore[no-any-return]
                    uow,
                    user_id,
                    model.UploadJob,
                    CrudOperation.UPDATE_ONE,
                    objs=updated_job,
                )
