import cProfile
import logging
import os
import pstats
import sys
import test.test_client.util as test_util
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning
from test.test_client.service_test_client import ServiceTestClient
from test.test_client.util import parse_stats

import pandas as pd

from gen_epix.casedb.domain import command, enum
from gen_epix.fastapp import CrudOperation

PERFORMANCE_DF = []


class TestRead:

    def test_read_case_sets(self):
        test_name = sys._getframe().f_code.co_name
        df = {}
        for repository_type in enum.RepositoryType:
            if repository_type in (enum.RepositoryType.SA_SQL,):
                continue
            test_util.set_log_level("casedb", logging.ERROR)
            env = ServiceTestClient.get_test_client(
                test_type=EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
                repository_type=repository_type,
                log_level=logging.ERROR,
            )
            # TODO: set logger
            with cProfile.Profile() as profiler:

                user = test_util.create_root_user_from_claims(env.cfg, env.app)
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
            parse_stats(PERFORMANCE_DF, stats, repository_type=repository_type.value)

    def test_tear_down(self):
        # TODO: tearDownClass should be called by the test framework instead
        TestRead.tearDownClass()

    @classmethod
    def tearDownClass(cls):
        test_dir = ServiceTestClient.get_test_client(
            test_type=EnumTestType.CASEDB_PERFORMANCE_REPOSITORY,
            repository_type=enum.RepositoryType.DICT,
        ).test_dir
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(
            os.path.join(test_dir, cls.__name__) + ".performance.csv", index=False
        )
        df.to_excel(
            os.path.join(test_dir, cls.__name__) + ".performance.xlsx", index=False
        )
