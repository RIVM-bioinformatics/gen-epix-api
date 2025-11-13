import cProfile
import logging
import pstats
from pathlib import Path

import pandas as pd
import pyinstrument

from gen_epix.commondb.test.util import parse_stats

PERFORMANCE_DF: list = []
PERFORMANCE_HTML: list = []


class TestStartup:
    USER_JOURNEYS = None

    def test_startup_pyinstrument(self) -> None:
        profiler = pyinstrument.Profiler(async_mode="enabled")
        profiler.start()

        from test.test_client.app_test_client import ServiceTestClient
        from test.test_client.enum import (
            TestType as EnumTestType,
        )  # to avoid pytest warning

        from gen_epix.casedb.domain import enum
        from gen_epix.casedb.domain.enum import RepositoryType

        repository_type = RepositoryType.DICT
        _ = ServiceTestClient.get_test_client(
            test_type=EnumTestType.CASEDB_PERFORMANCE_STARTUP,
            repository_type=repository_type,
            log_level=logging.ERROR,
        )
        profiler.stop()
        PERFORMANCE_HTML.append(profiler.output_html())

    def test_startup_cprofile(self) -> None:
        with cProfile.Profile() as profiler:
            from test.test_client.app_test_client import ServiceTestClient
            from test.test_client.enum import (
                TestType as EnumTestType,
            )  # to avoid pytest warning

            from gen_epix.casedb.domain.enum import RepositoryType

            repository_type = RepositoryType.SA_SQLITE
            _ = ServiceTestClient.get_test_client(
                test_type=EnumTestType.CASEDB_PERFORMANCE_STARTUP,
                repository_type=repository_type,
                log_level=logging.ERROR,
            )
            stats = pstats.Stats(profiler)
            stats.sort_stats("tottime")
            # stats.print_stats(5)
            parse_stats(PERFORMANCE_DF, stats, repository_type=repository_type.value)

    def test_tear_down(self) -> None:
        # TODO: tearDownClass should be called by the test framework instead
        TestStartup.tearDownClass()

    @classmethod
    def tearDownClass(cls) -> None:
        from test.test_client.app_test_client import ServiceTestClient
        from test.test_client.enum import (
            TestType as EnumTestType,
        )  # to avoid pytest warning

        from gen_epix.casedb.domain.enum import RepositoryType

        test_dir = ServiceTestClient.get_test_client(
            test_type=EnumTestType.CASEDB_PERFORMANCE_STARTUP,
            repository_type=RepositoryType.DICT,
        ).test_dir
        with open(Path(test_dir) / f"{cls.__name__}.performance.html", "w") as f:
            f.write("".join(PERFORMANCE_HTML))
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(Path(test_dir) / f"{cls.__name__}.performance.csv", index=False)
        df.to_excel(Path(test_dir) / f"{cls.__name__}.performance.xlsx", index=False)

    # @classmethod
    # def tearDownClass(cls):
    #     test_dir = ServiceTestClient.get_service_test_client(
    #         test_type=EnumTestType.PERFORMANCE_STARTUP,
    #         repository_type=enum.RepositoryType.DICT,
    #     ).test_dir
    #     df = pd.DataFrame.from_records(PERFORMANCE_DF)
    #     df.to_csv(
    #         Path(test_dir) / f"{cls.__name__}.performance.csv", index=False
    #     )
    #     df.to_excel(
    #         Path(test_dir) / f"{cls.__name__}.performance.xlsx", index=False
    #     )
