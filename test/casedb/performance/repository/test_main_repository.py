import cProfile
import logging
import pstats
import sys
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning

import pandas as pd

import gen_epix.common.test.util as test_util
from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import CrudOperation

PERFORMANCE_DF: list[dict] = []


class TestRead:

    def test_read_case_sets(self) -> None:
        test_name = sys._getframe().f_code.co_name
        for repository_type in enum.RepositoryType:
            if repository_type in (enum.RepositoryType.SA_SQL,):
                continue
            test_util.set_log_level("casedb", logging.ERROR)
            env = CasedbTestClient.get_test_client(
                test_type=EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
                repository_type=repository_type,
                log_level=logging.ERROR,
            )
            # TODO: set logger
            with cProfile.Profile() as profiler:

                user: model.User = test_util.create_root_user_from_claims(
                    env.cfg, env.app
                )
                for i in range(100):
                    case_sets = env.app.handle(
                        command.CaseSetCrudCommand(
                            user=user,
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
        # TODO: tearDownClass should be called by the test framework instead
        TestRead.tearDownClass()

    @classmethod
    def tearDownClass(cls) -> None:
        test_dir = CasedbTestClient.get_test_client(
            test_type=EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
            repository_type=enum.RepositoryType.DICT,
        ).test_dir
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(Path(test_dir) / f"{cls.__name__}.performance.csv", index=False)
        df.to_excel(Path(test_dir) / f"{cls.__name__}.performance.xlsx", index=False)
