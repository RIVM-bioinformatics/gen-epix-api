"""Tests for batch uploads running concurrently with other uploads.

Concurrent uploads deadlocked (SQL Server 1205) because the batch ran under
SERIALIZABLE, where the existence checks take range locks on every new id. The
upload now runs under READ COMMITTED and retries a transaction that conflicts
with a concurrent one.
"""

from test.util.mock_compat import Mock
from typing import Any, ClassVar

import pytest
from pydantic import BaseModel

from gen_epix.casedb.domain import command as casedb_command
from gen_epix.casedb.services.case.upload import CaseBatchUploader
from gen_epix.commondb.domain import command
from gen_epix.commondb.services import upload as upload_module
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp import IsolationLevel, exc


class _Batch(BaseModel):
    items: list[int]


class _UploadCommand(command.Command):
    NAME: ClassVar[str] = "test_upload_command"
    batch: _Batch


class _Uploader(BatchUploader):
    """Uploader whose single attempt is scripted by the test."""

    def __init__(self, failures: list[Exception]) -> None:
        # Deliberately not calling super().__init__: only the retry loop is tested
        # pylint: disable=super-init-not-called
        self.failures = list(failures)
        self.seen_items: list[list[int]] = []
        self.cmd_batch_field_name = "batch"
        self.service = Mock()
        self.service._logger = None

    def verify_user_rights(self, cmd: Any) -> None:
        pass

    def _upload_batch_once(self, cmd: Any) -> Any:
        self.seen_items.append(list(cmd.batch.items))
        # Simulate the upload mutating the batch before the transaction fails
        cmd.batch.items.append(99)
        if self.failures:
            raise self.failures.pop(0)
        return "result"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(upload_module.time, "sleep", lambda _seconds: None)


def _cmd() -> _UploadCommand:
    return _UploadCommand(batch=_Batch(items=[1, 2]))


@pytest.mark.parametrize(
    "failure",
    [
        exc.ConcurrentModificationError("x", "deadlock"),
        exc.UniqueConstraintViolationError("x", "duplicate key"),
    ],
)
def test_conflicting_transaction_is_retried_on_a_pristine_batch(
    failure: Exception,
) -> None:
    uploader = _Uploader([failure])

    assert uploader.upload_batch(_cmd()) == "result"  # type: ignore[arg-type]
    assert uploader.seen_items == [[1, 2], [1, 2]]


def test_retry_gives_up_after_max_attempts() -> None:
    failures = [
        exc.ConcurrentModificationError("x", "deadlock")
        for _ in range(BatchUploader.MAX_UPLOAD_ATTEMPTS)
    ]
    uploader = _Uploader(failures)

    with pytest.raises(exc.ConcurrentModificationError):
        uploader.upload_batch(_cmd())  # type: ignore[arg-type]
    assert len(uploader.seen_items) == BatchUploader.MAX_UPLOAD_ATTEMPTS


def test_other_errors_are_not_retried() -> None:
    uploader = _Uploader([ValueError("bad data")])

    with pytest.raises(ValueError, match="bad data"):
        uploader.upload_batch(_cmd())  # type: ignore[arg-type]
    assert len(uploader.seen_items) == 1


def test_no_retry_when_uploader_disallows_it() -> None:
    uploader = _Uploader([exc.ConcurrentModificationError("x", "deadlock")])
    uploader.can_retry_batch = lambda _cmd: False  # type: ignore[method-assign]

    with pytest.raises(exc.ConcurrentModificationError):
        uploader.upload_batch(_cmd())  # type: ignore[arg-type]
    assert len(uploader.seen_items) == 1


@pytest.mark.parametrize("has_samples", [True, False])
def test_case_batch_with_samples_is_not_retried(has_samples: bool) -> None:
    """Samples are committed in seqdb mid-transaction; a retry would repeat them."""
    cmd = Mock(spec=casedb_command.UploadCasesCommand)
    cmd.case_batch = Mock()
    cmd.case_batch.has_samples.return_value = has_samples

    can_retry = CaseBatchUploader.can_retry_batch(Mock(spec=CaseBatchUploader), cmd)

    assert can_retry is not has_samples


def test_upload_transaction_runs_under_read_committed() -> None:
    """SERIALIZABLE range locks on new ids made concurrent uploads deadlock."""

    class _StopUpload(Exception):
        pass

    uow_kwargs: dict[str, Any] = {}

    def uow(**kwargs: Any) -> Any:
        uow_kwargs.update(kwargs)
        raise _StopUpload()

    uploader = BatchUploader.__new__(BatchUploader)
    uploader.service = Mock()
    uploader.service.repository.uow.side_effect = uow
    uploader.init_batch_upload_result = Mock()  # type: ignore[method-assign]

    with pytest.raises(_StopUpload):
        uploader._upload_batch_once(_cmd())  # type: ignore[arg-type]  # pylint: disable=protected-access

    assert uow_kwargs == {"isolation_level": IsolationLevel.READ_COMMITTED}
