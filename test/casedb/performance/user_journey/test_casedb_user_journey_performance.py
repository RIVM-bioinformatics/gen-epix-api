import cProfile
import logging
import pickle
import pstats
import re
import sys
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient
from test.test_client.enum import (
    EnumTestType as EnumTestType,  # to avoid pytest warning
)
from test.test_client.log_parser_v1 import V1LogParser
from test.test_client.log_parser_v2 import V2LogParser
from test.test_client.user_journey_v1 import UserJourneyColumn as V1UserJourneyColumn
from test.test_client.user_journey_v2 import UserJourneyColumn as V2UserJourneyColumn
from test.test_client.util import get_test_root_output_dir

import pandas as pd
import pyinstrument
import pytest

import gen_epix.commondb.test.util as test_util
from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import enum as seqdb_enum

PERFORMANCE_DF: list = []
PERFORMANCE_HTML: dict = {}
V1_USER_JOURNEY_FILE_PREFIX = "v1.user_journey"
V2_USER_JOURNEY_FILE_PREFIX = "v2.user_journey"
USER_JOURNEY_DIR = Path(__file__).parent

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY,
)

CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.mark.scenario_ids("TC-PERF-09-01")
@pytest.mark.skip(reason="Outdated test, keeping for reference")
class TestRead:
    USER_JOURNEYS = None

    def get_user_journeys(self) -> None:
        # TODO: add functionality to get only user journeys for a particular scenario (read, update, etc.)
        if TestRead.USER_JOURNEYS is None:
            TestRead.USER_JOURNEYS = []
            for file in USER_JOURNEY_DIR.iterdir():
                if not re.match(
                    r".*\.log\.txt(\.gz)?$", str(file), flags=re.IGNORECASE
                ):
                    continue
                src_file = file
                pkl_file = Path(str(file) + ".pkl.gz")
                if pkl_file.is_file():
                    if pkl_file.stat().st_mtime > src_file.stat().st_mtime:
                        TestRead.USER_JOURNEYS.append(pickle.load(open(pkl_file, "rb")))
                        continue
                    else:
                        pkl_file.unlink()
                if str(file).startswith(V1_USER_JOURNEY_FILE_PREFIX):
                    name = re.sub(
                        V1_USER_JOURNEY_FILE_PREFIX + r".*\.(\w+)\.log\.txt(\.gz)?$",
                        r"V1.\1",
                        str(file),
                        flags=re.IGNORECASE,
                    )
                    log_parser = V1LogParser(str(src_file))
                    log_parser.parse()
                    user_journey = log_parser.create_user_journey()
                    commands = user_journey.get_commands()[
                        V1UserJourneyColumn.COMMAND_OBJECT
                    ].tolist()
                elif str(file).startswith(V2_USER_JOURNEY_FILE_PREFIX):
                    name = re.sub(
                        V2_USER_JOURNEY_FILE_PREFIX + r"^.*\.(\w+)\..*$",
                        r"V2.\1",
                        str(file),
                        flags=re.IGNORECASE,
                    )
                    log_parser = V2LogParser(str(src_file))
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

        test_name = sys._getframe().f_code.co_name
        user_journeys = self.get_user_journeys()
        df = {}
        for user_journey in user_journeys:
            commands = user_journey["commands"]
            for repository_type in {
                DevRepositoryConfig.DICT_DEMO,
                DevRepositoryConfig.SA_SQLITE_DEMO,
            }:
                test_util.set_log_level("casedb", logging.ERROR)
                env = CasedbTestClient.get_test_client(
                    test_type=f"{EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY.value}__{repository_type.value}",
                    app_cfg=CASEDB_APP_CFGS[
                        f"{EnumTestType.CASEDB_PERFORMANCE_USER_JOURNEY.value}__{repository_type.value}"
                    ],
                    log_level=logging.ERROR,
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
                    test_util.parse_stats(
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
        test_dir = get_test_root_output_dir()
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(Path(test_dir) / f"{cls.__name__}.performance.csv", index=False)
        df.to_excel(Path(test_dir) / f"{cls.__name__}.performance.xlsx", index=False)
        for key, html_str in PERFORMANCE_HTML.items():
            with open(
                Path(test_dir) / f"{cls.__name__}.performance.{key}.html", "w"
            ) as f:
                f.write("".join(html_str))
