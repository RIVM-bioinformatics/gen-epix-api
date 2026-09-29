import cProfile
import logging
import pstats
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient
from test.test_client.enum import (
    EnumTestType as EnumTestType,  # to avoid pytest warning
)
from test.test_client.util import get_test_root_output_dir

import pandas as pd
import pyinstrument
import pytest

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.util import parse_stats
from gen_epix.seqdb.domain import enum as seqdb_enum

PERFORMANCE_DF: list = []
PERFORMANCE_HTML: list = []

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_STARTUP,
    log_any=False,
)

CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_STARTUP,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
    log_any=False,
)


@pytest.mark.scenario_ids("TC-PERF-09-01")
class TestStartup:
    USER_JOURNEYS = None

    def test_startup_pyinstrument(self) -> None:
        profiler = pyinstrument.Profiler(async_mode="enabled")
        profiler.start()

        repository_type = DevRepositoryConfig.DICT_DEMO
        _ = CasedbTestClient.get_test_client(
            test_type=f"{EnumTestType.CASEDB_PERFORMANCE_STARTUP.value}__{repository_type.value}",
            app_cfg=CASEDB_APP_CFGS[
                f"{EnumTestType.CASEDB_PERFORMANCE_STARTUP.value}__{repository_type.value}"
            ],
            log_level=logging.ERROR,
        )
        profiler.stop()
        PERFORMANCE_HTML.append(profiler.output_html())

    def test_startup_cprofile(self) -> None:
        with cProfile.Profile() as profiler:
            repository_type = DevRepositoryConfig.SA_SQLITE_DEMO
            _ = CasedbTestClient.get_test_client(
                test_type=f"{EnumTestType.CASEDB_PERFORMANCE_STARTUP.value}__{repository_type.value}",
                app_cfg=CASEDB_APP_CFGS[
                    f"{EnumTestType.CASEDB_PERFORMANCE_STARTUP.value}__{repository_type.value}"
                ],
                log_level=logging.ERROR,
            )
            stats = pstats.Stats(profiler)
            stats.sort_stats("tottime")
            # stats.print_stats(5)
            parse_stats(PERFORMANCE_DF, stats, repository_type=repository_type.value)

    def test_tear_down(self) -> None:
        # TODO: finalize_outputs should be called by the test framework instead
        TestStartup.finalize_outputs()

    @classmethod
    def finalize_outputs(cls) -> None:
        test_dir = get_test_root_output_dir()
        with open(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.startup.html", "w"
        ) as f:
            f.write("".join(PERFORMANCE_HTML))
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.startup.csv",
            index=False,
        )
        df.to_excel(
            Path(test_dir) / f"{cls.__name__}.casedb.performance.startup.xlsx",
            index=False,
        )
