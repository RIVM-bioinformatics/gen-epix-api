"""Tests for per-thread request state now that route handlers run in a threadpool.

Route handlers run concurrently in FastAPI's threadpool. State that tracks "the
current request" (the unit-of-work stack of a repository and the command stack of
the app) must therefore be per thread, or one request sees another's state.
"""

import threading
from collections.abc import Callable
from test.util.mock_compat import Mock
from typing import Any, ClassVar

import pytest
import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork

_TIMEOUT = 5


class _BlockingCommand(Command):
    NAME: ClassVar[str] = "test_blocking_command"


class _OtherCommand(Command):
    NAME: ClassVar[str] = "test_other_command"


def _run_while_other_thread_holds(
    hold: Callable[[threading.Event, threading.Event], None],
    action: Callable[[], Any],
) -> Any:
    """Run *action* while another thread is inside *hold*."""
    entered = threading.Event()
    release = threading.Event()
    errors: list[BaseException] = []

    def target() -> None:
        try:
            hold(entered, release)
        except BaseException as exception:  # pylint: disable=broad-exception-caught
            errors.append(exception)
            entered.set()

    thread = threading.Thread(target=target)
    thread.start()
    try:
        assert entered.wait(_TIMEOUT)
        return action()
    finally:
        release.set()
        thread.join(_TIMEOUT)
        assert not errors, errors


@pytest.fixture(name="repo")
def repository_fixture() -> SARepository:
    """Provide a SQLite repository without mappers."""
    return SARepository(sa.create_engine("sqlite://"), register_mappers=False)


def test_uow_on_another_thread_is_not_nested(repo: SARepository) -> None:
    """A unit of work open on another thread must not be reused as outer context."""
    sessions: dict[str, Any] = {}

    def hold(entered: threading.Event, release: threading.Event) -> None:
        with repo.uow() as uow:
            sessions["other"] = uow.session  # type: ignore[attr-defined]
            entered.set()
            release.wait(_TIMEOUT)

    def action() -> None:
        with repo.uow() as uow:
            sessions["this"] = uow.session  # type: ignore[attr-defined]

    _run_while_other_thread_holds(hold, action)

    assert sessions["this"] is not sessions["other"]


def test_uow_on_same_thread_is_still_nested(repo: SARepository) -> None:
    with repo.uow() as outer:
        with repo.uow() as inner:
            assert inner.session is outer.session  # type: ignore[attr-defined]


def test_detached_uow_does_not_join_or_affect_the_stack(repo: SARepository) -> None:
    with repo.uow() as outer:
        with repo.uow(detached=True) as detached:
            assert detached.session is not outer.session  # type: ignore[attr-defined]
            with repo.uow() as inner:
                assert inner.session is outer.session  # type: ignore[attr-defined]
    assert repo._uow_context_stack == []  # pylint: disable=protected-access


def test_detached_uow_can_be_exited_on_another_thread(repo: SARepository) -> None:
    """A streaming generator may be resumed on a different threadpool thread."""
    uow = repo.uow(detached=True)
    entered = threading.Thread(target=uow.__enter__)
    entered.start()
    entered.join(_TIMEOUT)

    uow.__exit__(None, None, None)

    assert repo._uow_context_stack == []  # pylint: disable=protected-access


def test_command_on_another_thread_still_gets_policies_applied() -> None:
    """A command must be initial, and thus authorized, regardless of other threads.

    Whether policies are enforced depends on the command stack depth. With a
    shared stack, a request arriving while another request's command is being
    handled would be treated as a nested, trusted command and skip authorization.
    """
    app = App(logger=None, pdp=Mock())
    app.pdp.apply.return_value = None  # type: ignore[union-attr]
    blocking: dict[str, threading.Event] = {}
    app.register_handler(
        _BlockingCommand,
        lambda _cmd: (blocking["entered"].set(), blocking["release"].wait(_TIMEOUT)),
    )
    app.register_handler(_OtherCommand, lambda _cmd: "handled")
    initial_commands: list[Command] = []
    handle_initial_command = (
        app._handle_initial_command
    )  # pylint: disable=protected-access

    def record_initial_command(cmd: Command) -> None:
        initial_commands.append(cmd)
        handle_initial_command(cmd)

    app._handle_initial_command = record_initial_command  # type: ignore[method-assign]

    def hold(entered: threading.Event, release: threading.Event) -> None:
        blocking["entered"] = entered
        blocking["release"] = release
        app.handle(_BlockingCommand())

    other_cmd = _OtherCommand()
    _run_while_other_thread_holds(hold, lambda: app.handle(other_cmd))

    assert other_cmd in initial_commands
    assert app._command_stack == []  # pylint: disable=protected-access


def test_dict_repository_serializes_crud_calls() -> None:
    """In-memory dicts are not safe for concurrent iteration and mutation."""
    repository = DictRepository.__new__(DictRepository)
    acquired_by_other_thread: list[bool] = []

    def hold(entered: threading.Event, release: threading.Event) -> None:
        def crud(*_args: Any, **_kwargs: Any) -> None:
            entered.set()
            release.wait(_TIMEOUT)

        repository._crud = crud  # type: ignore[method-assign]
        repository.crud(None, None, None, None)  # type: ignore[arg-type]

    def action() -> None:
        lock = DictRepository._CRUD_LOCK  # pylint: disable=protected-access
        acquired = lock.acquire(blocking=False)
        if acquired:
            lock.release()
        acquired_by_other_thread.append(acquired)

    _run_while_other_thread_holds(hold, action)

    assert acquired_by_other_thread == [False]


class _OdbcError(Exception):
    """Stand-in for pyodbc.Error, whose first argument is the SQLSTATE."""


@pytest.mark.parametrize(
    "orig",
    [
        _OdbcError(
            "40001",
            "[40001] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]"
            "Transaction (Process ID 89) was deadlocked on lock resources with "
            "another process and has been chosen as the deadlock victim. Rerun the "
            "transaction. (1205) (SQLExecDirectW)",
        ),
        _OdbcError("HY000", "... deadlock victim ... (1205) (SQLExecDirectW)"),
    ],
)
def test_deadlock_becomes_concurrent_modification_error(orig: Exception) -> None:
    error = sa_exc.DBAPIError("INSERT ...", {}, orig)

    with pytest.raises(exc.ConcurrentModificationError) as exc_info:
        SAUnitOfWork._handle_exception(  # pylint: disable=protected-access
            type(error), error, None
        )

    assert exc_info.value.get_http_status_code() == 409


def test_other_statement_error_is_unchanged() -> None:
    error = sa_exc.DBAPIError("INSERT ...", {}, _OdbcError("42S02", "Invalid object"))

    with pytest.raises(ValueError, match="Statement error"):
        SAUnitOfWork._handle_exception(  # pylint: disable=protected-access
            type(error), error, None
        )
