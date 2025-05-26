import cProfile
import os
import pstats
import uuid
from test.fastapp.command import Model2_2CrudCommand
from test.fastapp.enum import TestType as EnumTestType  # to avoid PyTest warning
from test.fastapp.model import Model2_2
from test.fastapp.service_test_client import ServiceTestClient as Env
from test.fastapp.util import parse_stats

import pandas as pd
import pyinstrument
import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository


def get_test_clients() -> list[Env]:
    envs = [
        Env.get_test_client(
            DictRepository, test_type=EnumTestType.SERVICE_SERVICE_UNIT_REPOSITORY
        )
    ]
    envs.append(
        Env.get_test_client(
            SARepository,
            test_type=EnumTestType.SERVICE_SERVICE_UNIT_REPOSITORY,
            test_name=envs[0].test_name,
        )
    )
    return envs


PERFORMANCE_DF: list = []
PERFORMANCE_HTML: dict = {}


@pytest.mark.parametrize(
    "env",
    get_test_clients(),
)
class TestRepository:

    def test_create_some(self, env: Env) -> None:
        _, _, bg_models2_1, _ = env.create_all_model_instances()

        # for iteration in range(1):
        #     for n_models in [1]:
        #         for content_size in [1]:
        for iteration in range(10):
            for n_models in [1, 10, 100, 1000]:
                for content_size in [1, 10, 100]:
                    models2_2 = [
                        env.get_model_instance_for_class(Model2_2, set_id=False)
                        for _ in range(n_models)
                    ]
                    for model2_2 in models2_2:
                        model2_2.var3 = {
                            str(uuid.uuid4()): str(uuid.uuid4())
                            for _ in range(content_size)
                        }
                        model2_2.model2_1_id = bg_models2_1[0].id

                    # Monitor performance using cProfile
                    with cProfile.Profile() as profiler:
                        models2_2_created = env.app.handle(
                            Model2_2CrudCommand(
                                objs=models2_2, operation=CrudOperation.CREATE_SOME
                            )
                        )
                    stats = pstats.Stats(profiler)
                    stats.sort_stats("tottime")
                    parse_stats(
                        PERFORMANCE_DF,
                        stats,
                        test_name=env.test_name,
                        repository_type=env.repository_type,
                        n_models=n_models,
                        content_size=content_size,
                        iteration=iteration,
                    )
                    # Monitor performance using pyinstrument
                    for model2_2 in models2_2:
                        model2_2.id = None
                    profiler = pyinstrument.Profiler(async_mode="enabled")
                    profiler.start()
                    models2_2_created = env.app.handle(
                        Model2_2CrudCommand(
                            objs=models2_2, operation=CrudOperation.CREATE_SOME
                        )
                    )
                    profiler.stop()
                    key = f"{env.repository_type}.{n_models}.{content_size}.{iteration}"
                    PERFORMANCE_HTML[key] = profiler.output_html()

    def test_tear_down(self, env: Env) -> None:
        # TODO: tearDownClass should be called by the test framework instead
        TestRepository.tearDownClass(env)

    @classmethod
    def tearDownClass(cls, env):
        if env.repository_type != get_test_clients()[-1].repository_type:
            # Only execute for the last repository class
            return
        test_dir = env.test_dir
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
