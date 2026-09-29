import logging
import random
import time
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.performance.retrieve_stats.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from uuid import UUID

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.util import profile_method

TARGET_USER_KEY = "lsppoc.rivm6@rivmnl.onmicrosoft.com"

ITERATIONS = 50
PROFILE_ITERATION = random.randrange(ITERATIONS)

# Collect execution times for the performance summary.
EXECUTION_TIMES: list[float] = []


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
    client = Env.get_test_client(
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )
    return client  # type: ignore[return-value]


@pytest.fixture(scope="module", name="user_for_test")
def get_user_for_test(env: Env) -> model.User:
    """Fetch and return the target organization user once per test module."""
    return env.get_root_user(TARGET_USER_KEY)  # type: ignore[return-value]


@pytest.fixture(scope="module", name="all_case_type_ids")
def get_all_case_type_ids(
    env: Env,
    user_for_test: model.User,
) -> list[UUID]:
    """Fetch and return all case type IDs once per test module."""
    case_types: list[model.CaseType] = env.app.handle(
        command.CaseTypeCrudCommand(
            operation=CrudOperation.READ_ALL,
            user=user_for_test,
        )
    )
    case_type_ids = [
        case_type.id for case_type in case_types if case_type.id is not None
    ]
    allowed_ids: list[UUID] = []
    for case_type_id in case_type_ids:
        try:
            retrieve_case_type_stats(
                env,
                {case_type_id},
                user_for_test,
            )
            allowed_ids.append(case_type_id)
        except exc.UnauthorizedAuthError:
            continue

    return allowed_ids


def retrieve_case_type_stats(
    env: Env,
    case_type_ids: set[UUID],
    user: model.User,
) -> list[model.CaseStats]:
    return env.app.handle(
        command.RetrieveCaseTypeStatsCommand(
            user=user,
            case_type_ids=case_type_ids,
        )
    )


@profile_method(path=None)
def retrieve_case_type_stats_profiled(
    env: Env,
    case_type_ids: set[UUID],
    user: model.User,
) -> list[model.CaseStats]:
    """Profiled version of retrieve_case_type_stats."""
    return retrieve_case_type_stats(env, case_type_ids, user)


@pytest.mark.parametrize("batch_ratio", [1.0])
@pytest.mark.parametrize("iteration", range(ITERATIONS))
def test_retrieve_case_type_stats_scaled_profiled(
    env: Env,
    user_for_test: model.User,
    all_case_type_ids: list[UUID],
    batch_ratio: float,
    iteration: int,
) -> None:
    subset_size = max(1, int(len(all_case_type_ids) * batch_ratio))
    target_ids = set(all_case_type_ids[:subset_size])

    start_time = time.perf_counter()

    if iteration == PROFILE_ITERATION:
        stats = retrieve_case_type_stats_profiled(
            env,
            target_ids,
            user_for_test,
        )
        profile_marker = " | PROFILED"
    else:
        stats = retrieve_case_type_stats(
            env,
            target_ids,
            user_for_test,
        )
        profile_marker = ""

    duration = time.perf_counter() - start_time

    EXECUTION_TIMES.append(duration)

    print(
        f"[Run {iteration + 1}/{ITERATIONS}] "
        f"Batch Ratio: {batch_ratio * 100:.0f}% "
        f"({len(target_ids)} IDs) -> "
        f"Took {duration:.4f}s | "
        f"Returned {len(stats)} stats"
        f"{profile_marker}"
    )

    # Print the summary after the final iteration.
    if iteration == ITERATIONS - 1:
        average_time = sum(EXECUTION_TIMES) / len(EXECUTION_TIMES)

        print(
            "\n"
            f"{'=' * 70}\n"
            "Performance Summary\n"
            f"{'=' * 70}\n"
            f"Iterations:       {len(EXECUTION_TIMES)}\n"
            f"Average time:     {average_time:.4f}s\n"
            f"Min time:         {min(EXECUTION_TIMES):.4f}s\n"
            f"Max time:         {max(EXECUTION_TIMES):.4f}s\n"
            f"Total time:       {sum(EXECUTION_TIMES):.4f}s\n"
            f"{'=' * 70}"
        )
