import cProfile
import logging
import pstats
import sys
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient
from test.test_client.enum import (
    EnumTestType as EnumTestType,  # to avoid PyTest warning
)
from test.test_client.util import get_test_root_output_dir

import pandas as pd
import pytest

import gen_epix.commondb.test.util as test_util
from gen_epix.casedb.domain import command, enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

PERFORMANCE_DF: list[dict] = []

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
    log_any=False,
)

CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
    log_any=False,
)


@pytest.mark.scenario_ids("TC-PERF-09-01")
class TestRead:

    def test_read_case_sets(self) -> None:
        test_name = sys._getframe().f_code.co_name
        for repository_type in DevRepositoryConfig:
            if repository_type in [
                DevRepositoryConfig.SA_SQL,
            ]:
                continue
            test_util.set_log_level("casedb", logging.ERROR)
            env = CasedbTestClient.get_test_client(  # type: ignore[return-value]
                test_type=f"{EnumTestType.CASEDB_PERFORMANCE_REPOSITORY.value}__{repository_type.value}",
                app_cfg=CASEDB_APP_CFGS[
                    f"{EnumTestType.CASEDB_PERFORMANCE_REPOSITORY.value}__{repository_type.value}"
                ],
                verbose=False,
                log_level=logging.ERROR,
                use_endpoints=False,
            )
            # TODO: set logger
            with cProfile.Profile() as profiler:
                for i in range(100):
                    case_sets = env.app.handle(
                        command.CaseSetCrudCommand(
                            user=env.get_root_user(),
                            operation=CrudOperation.READ_ALL,
                        )
                    )

            stats = pstats.Stats(profiler)
            stats.sort_stats("tottime")
            # stats.print_stats(5)
            test_util.parse_stats(
                PERFORMANCE_DF, stats, repository_type=repository_type.value
            )

    def test_tear_down(self) -> None:
        # TODO: finalize_outputs should be called by the test framework instead
        TestRead.finalize_outputs()

    @classmethod
    def finalize_outputs(cls) -> None:
        test_dir = get_test_root_output_dir()
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.repository.csv",
            index=False,
        )
        df.to_excel(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.repository.xlsx",
            index=False,
        )
        df.to_csv(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.repository.csv",
            index=False,
        )
        df.to_excel(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.repository.xlsx",
            index=False,
        )
