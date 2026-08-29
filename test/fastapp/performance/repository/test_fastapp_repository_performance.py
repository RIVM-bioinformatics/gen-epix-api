import cProfile
import pstats
from pathlib import Path
from test.fastapp.command import Model2_2CrudCommand
from test.fastapp.enum import TestType as EnumTestType  # to avoid PyTest warning
from test.fastapp.model import DOMAIN, Model2_2
from test.fastapp.service_test_client import ServiceTestClient as Env
from test.fastapp.util import parse_stats
from test.test_client.util import get_test_name, get_test_root_output_dir

import pandas as pd
import pyinstrument
import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository

REPOSITORY_CLASSES = [DictRepository, SARepository]
PERFORMANCE_TEST_NAME = get_test_name(
    EnumTestType.SERVICE_SERVICE_PERFORMANCE_REPOSITORY
)


@pytest.fixture(params=REPOSITORY_CLASSES)
def env(request: pytest.FixtureRequest) -> Env:
    return Env.get_test_client(
        request.param,
        domain=DOMAIN,
        test_type=EnumTestType.SERVICE_SERVICE_PERFORMANCE_REPOSITORY,
        test_name=PERFORMANCE_TEST_NAME,
    )


PERFORMANCE_DF: list = []
PERFORMANCE_HTML: dict = {}


class TestRepository:

    def test_create_some(self, env: Env) -> None:
        _, _, bg_models2_1, _ = env.create_all_model_instances()

        # for iteration in range(1):
        #     for n_models in [1]:
        #         for content_size in [1]:
        for iteration in range(10):
            for n_models in [1, 10, 100, 1000]:
                for content_size in [1, 10, 100]:
                    models2_2: list[Model2_2] = [
                        env.get_model_instance_for_class(Model2_2, set_id=False)
                        for _ in range(n_models)
                    ]
                    for model2_2 in models2_2:
                        # model2_2.var3 = {
                        #     str(uuid.uuid4()): str(uuid.uuid4())
                        #     for _ in range(content_size)
                        # }
                        # Create randomized string of length content_size
                        model2_2.var2 = "".join(
                            [chr(65 + (i % 26)) for i in range(content_size)]
                        )
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
        # TODO: finalize_outputs should be called by the test framework instead
        TestRepository.finalize_outputs(env)

    @classmethod
    def finalize_outputs(cls, env):
        if env.repository_type != SARepository.__name__:
            # Only execute for the last repository class
            return
        test_dir = get_test_root_output_dir()
        df = pd.DataFrame.from_records(PERFORMANCE_DF)
        df.to_csv(
            Path(test_dir) / f"{cls.__name__}.fastapp.performance.repository.csv",
            index=False,
        )
        df.to_excel(
            Path(test_dir) / f"{cls.__name__}.fastapp.performance.repository.xlsx",
            index=False,
        )
        # for key, html_str in PERFORMANCE_HTML.items():
        #     with open(
        #         Path(test_dir) / f"{cls.__name__}.fastapp.performance.repository.{key}.html", "w"
        #     ) as f:
        #         f.write("".join(html_str))
