import cProfile
import logging
import os
import pickle
import pstats
import re
import sys
import test.test_client.util as test_util
from test.test_client.enum import TestType as EnumTestType  # to avoid pytest warning
from test.test_client.log_parser_v1 import V1LogParser
from test.test_client.log_parser_v2 import V2LogParser
from test.test_client.service_test_client import ServiceTestClient
from test.test_client.user_journey_v1 import UserJourneyColumn as V1UserJourneyColumn
from test.test_client.user_journey_v2 import UserJourneyColumn as V2UserJourneyColumn
from test.test_client.util import parse_stats

import pandas as pd
import pyinstrument

from gen_epix.casedb.domain import enum

PERFORMANCE_DF: list = []
PERFORMANCE_HTML: dict = {}
V1_USER_JOURNEY_FILE_PREFIX = "v1.user_journey"
V2_USER_JOURNEY_FILE_PREFIX = "v2.user_journey"
USER_JOURNEY_DIR = os.path.join(
    os.path.dirname(test_util.__file__), "data", "user_journey"
)


class TestRead:
    USER_JOURNEYS = None

    def get_user_journeys(self) -> None:
        # TODO: add functionality to get only user journeys for a particular scenario (read, update, etc.)
        if TestRead.USER_JOURNEYS is None:
            TestRead.USER_JOURNEYS = []
            for file in os.listdir(USER_JOURNEY_DIR):
                if not re.match(r".*\.log\.txt(\.gz)?$", file, flags=re.IGNORECASE):
                    continue
                src_file = os.path.join(USER_JOURNEY_DIR, file)
                pkl_file = os.path.join(src_file + ".pkl.gz")
                if os.path.isfile(pkl_file):
                    if os.path.getmtime(pkl_file) > os.path.getmtime(src_file):
                        TestRead.USER_JOURNEYS.append(pickle.load(open(pkl_file, "rb")))
                        continue
                    else:
                        os.remove(pkl_file)
                if file.startswith(V1_USER_JOURNEY_FILE_PREFIX):
                    name = re.sub(
                        V1_USER_JOURNEY_FILE_PREFIX + r".*\.(\w+)\.log\.txt(\.gz)?$",
                        r"V1.\1",
                        file,
                        flags=re.IGNORECASE,
                    )
                    log_parser = V1LogParser(src_file)
                    log_parser.parse()
                    user_journey = log_parser.create_user_journey()
                    commands = user_journey.get_commands()[
                        V1UserJourneyColumn.COMMAND_OBJECT
                    ].tolist()
                elif file.startswith(V2_USER_JOURNEY_FILE_PREFIX):
                    name = re.sub(
                        V2_USER_JOURNEY_FILE_PREFIX + r"^.*\.(\w+)\..*$",
                        r"V2.\1",
                        file,
                        flags=re.IGNORECASE,
                    )
                    log_parser = V2LogParser(src_file)
                    log_parser.parse()
                    user_journey = log_parser.create_user_journey()
                    commands = user_journey.get_commands()[
                        V2UserJourneyColumn.COMMAND_OBJECT
                    ].tolist()
                else:
                    continue
                data = {
                    "name": name,
                    "src_file": src_file,
                    "commands": commands,
                }
                with open(pkl_file, "wb") as f:
                    pickle.dump(data, f)
                TestRead.USER_JOURNEYS.append(data)
        return TestRead.USER_JOURNEYS

    def test_journeys(self) -> None:

        from test.test_client.enum import (
            TestType as EnumTestType,  # to avoid pytest warning
        )
        from test.test_client.service_test_client import ServiceTestClient

        from gen_epix.casedb.domain import enum
        from gen_epix.casedb.domain.enum import RepositoryType

        test_name = sys._getframe().f_code.co_name
        user_journeys = self.get_user_journeys()
        df = {}
        for user_journey in user_journeys:
            commands = user_journey["commands"]
            for repository_type in {
                enum.RepositoryType.DICT,
                enum.RepositoryType.SA_SQLITE,
            }:
                test_util.set_log_level("casedb", logging.ERROR)
                env = ServiceTestClient.get_test_client(
                    test_type=EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY,
                    repository_type=repository_type,
                    log_level=logging.ERROR,
                    load_target="full",
                )
                # TODO: set logger
                for i in range(1):
                    # Monitor performance using cProfile
                    with cProfile.Profile() as profiler:
                        for command in commands:
                            env.app.handle(command)
                            command._policies = []
                    stats = pstats.Stats(profiler)
                    stats.sort_stats("tottime")
                    parse_stats(
                        PERFORMANCE_DF,
                        stats,
                        test_name=test_name,
                        repository_type=repository_type.value,
                        user_journey=user_journey["name"],
                        iteration=i,
                    )
                    # Monitor performance using pyinstrument
                    profiler = pyinstrument.Profiler(async_mode="enabled")
                    profiler.start()
                    for command in commands:
                        env.app.handle(command)
                        command._policies = []
                    profiler.stop()
                    key = f"{repository_type.value}.{user_journey['name']}.{i}"
                    PERFORMANCE_HTML[key] = profiler.output_html()

    def test_tear_down(self) -> None:
        # TODO: tearDownClass should be called by the test framework instead
        TestRead.tearDownClass()

    @classmethod
    def tearDownClass(cls) -> None:
        test_dir = ServiceTestClient.get_test_client(
            test_type=EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY,
            repository_type=enum.RepositoryType.DICT,
        ).test_dir
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(
            os.path.join(test_dir, cls.__name__) + ".performance.csv", index=False
        )
        df.to_excel(
            os.path.join(test_dir, cls.__name__) + ".performance.xlsx", index=False
        )
        for key, html_str in PERFORMANCE_HTML.items():
            with open(
                os.path.join(test_dir, cls.__name__) + f".performance.{key}.html", "w"
            ) as f:
                f.write("".join(html_str))
