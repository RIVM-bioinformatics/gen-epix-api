"""Reproduce CASEDB upload deadlocks against a preconfigured SQL database.

Run this test only while a SQL database instance is already running and has
reference data loaded, such as the PPR_TEST dataset. The test does not create
schemas, run migrations, seed data, or start database containers.
"""

import logging
import re
import threading
from concurrent.futures import Future, ThreadPoolExecutor, wait
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import EnumTestType
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = EnumTestType.CASEDB_PERFORMANCE_REPOSITORY
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQL
SKIP_ENDPOINTS = True
VERBOSE = False
ATTEMPTS = 5
ATTEMPT_TIMEOUT_SECONDS = 60

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """Build a CASEDB test client configured for the external SQL database."""
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.fixture(scope="module", name="user_for_test")
def get_user_for_test(env: Env) -> model.User:
    """Return the root user used to authorize reference-data reads and uploads."""
    return env.get_root_user()  # type: ignore[return-value]


def _get_upload_references(env: Env, user: model.User) -> tuple[UUID, UUID]:
    """Read a usable case type and data collection from the configured database.

    Args:
        env: CASEDB test client connected to the configured SQL database.
        user: Authorized user for reading reference data.

    Returns:
        The selected case type ID and data collection ID.

    Raises:
        AssertionError: If the database has no usable reference records.
    """
    case_types: list[model.CaseType] = env.app.handle(
        command.CaseTypeCrudCommand(
            operation=CrudOperation.READ_ALL,
            user=user,
        )
    )
    data_collections: list[model.DataCollection] = env.app.handle(
        command.DataCollectionCrudCommand(
            operation=CrudOperation.READ_ALL,
            user=user,
        )
    )
    case_type_id = next(
        (case_type.id for case_type in case_types if case_type.id is not None),
        None,
    )
    data_collection_id = next(
        (
            data_collection.id
            for data_collection in data_collections
            if data_collection.id is not None
        ),
        None,
    )
    if case_type_id is None or data_collection_id is None:
        raise AssertionError(
            "Configured SA_SQL database must contain a CaseType and DataCollection"
        )
    return case_type_id, data_collection_id


def _create_upload_command(
    user: model.User,
    case_type_id: UUID,
    data_collection_id: UUID,
) -> command.UploadCasesCommand:
    """Create a new minimal case-upload command with a fresh case ID."""
    case_id = uuid4()
    return command.UploadCasesCommand(
        user=user.model_copy(deep=True),
        case_type_id=case_type_id,
        default_created_in_data_collection_id=data_collection_id,
        case_batch=model.CaseBatchForUpload(
            cases=[
                model.CaseForUpload(
                    id=case_id,
                    case=model.Case(
                        id=case_id,
                        case_type_id=case_type_id,
                        created_in_data_collection_id=data_collection_id,
                        content={},
                    ),
                )
            ]
        ),
    )


def _run_upload(
    env: Env,
    upload_command: command.UploadCasesCommand,
    barrier: threading.Barrier,
) -> Any:
    """Synchronize with the peer worker and handle one upload command."""
    barrier.wait(timeout=ATTEMPT_TIMEOUT_SECONDS)
    return env.app.handle(upload_command)


def _classify_outcome(outcome: Any) -> str:
    """Return a diagnostic label for a successful or failed worker outcome."""
    if not isinstance(outcome, Exception):
        return "success"
    message = str(outcome)
    if re.search(r"\b1205\b", message) and "deadlock" in message.lower():
        return "sql-server-deadlock-1205"
    return f"{type(outcome).__name__}: {message}"


def _run_concurrent_attempt(
    env: Env,
    user: model.User,
    case_type_id: UUID,
    data_collection_id: UUID,
) -> list[Any]:
    """Run two fresh uploads concurrently and return both worker outcomes."""
    barrier = threading.Barrier(2)
    executor = ThreadPoolExecutor(max_workers=2)
    futures: list[Future[Any]] = [
        executor.submit(
            _run_upload,
            env,
            _create_upload_command(user, case_type_id, data_collection_id),
            barrier,
        )
        for _ in range(2)
    ]
    try:
        done, _ = wait(futures, timeout=ATTEMPT_TIMEOUT_SECONDS)
        outcomes: list[Any] = []
        for future in futures:
            if future not in done:
                outcomes.append(TimeoutError("upload timed out"))
                continue
            error = future.exception()
            outcomes.append(error if error is not None else future.result())
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
    return outcomes


def test_concurrent_case_upload_reproduces_sql_server_deadlock(
    env: Env,
    user_for_test: model.User,
) -> None:
    """Reproduce and identify SQL Server deadlock error 1205 within bounded attempts.

    Raises:
        AssertionError: If the configured database lacks required reference data.
        Failed: If no worker reports the target deadlock within the attempts.
    """
    case_type_id, data_collection_id = _get_upload_references(env, user_for_test)
    observed: list[str] = []

    for attempt in range(1, ATTEMPTS + 1):
        outcomes = _run_concurrent_attempt(
            env,
            user_for_test,
            case_type_id,
            data_collection_id,
        )
        classifications = [_classify_outcome(outcome) for outcome in outcomes]
        observed.append(f"attempt {attempt}: {classifications}")
        if "sql-server-deadlock-1205" in classifications:
            return

    pytest.fail(
        "SQL Server deadlock error 1205 was not reproduced within "
        f"{ATTEMPTS} attempts. Observed outcomes: {observed}"
    )
