import logging
from datetime import timedelta
from test.seqdb.integration.retrieve_samples.base import (
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from typing import ClassVar

import pytest

from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model

seqdb_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


@pytest.fixture(
    scope="module",
    name="env",
    params=[
        commondb_enum.DevRepositoryConfig.DICT_DEMO,
        commondb_enum.DevRepositoryConfig.SA_SQLITE_DEMO,
    ],
    ids=lambda x: x.value,
)
def env(request: pytest.FixtureRequest) -> Env:
    """Return a test client configured for either DICT or SA_SQLITE demo repos.

    The fixture is parameterized so the whole module runs against both
    repository backends. For the SA_SQLITE demo we respect `SKIP_ENDPOINTS`.
    """
    repository_type: commondb_enum.DevRepositoryConfig = request.param
    cfg_key = f"{TEST_TYPE.value}__{repository_type.value}"
    app_cfg = seqdb_APP_CFGS[cfg_key]

    use_endpoints = (
        not SKIP_ENDPOINTS
        if repository_type == commondb_enum.DevRepositoryConfig.SA_SQLITE_DEMO
        else True
    )

    return Env.get_test_client(  # type: ignore[return-value]
        test_type=f"{TEST_TYPE.value}__{repository_type.value}",
        app_cfg=app_cfg,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=use_endpoints,
    )


class TestRetrieveSamples:

    all_samples: ClassVar[list[model.Sample]] = []
    test_samples: ClassVar[list[model.Sample]] = []

    @pytest.fixture(scope="class", autouse=True)
    def _load_samples(self, request: pytest.FixtureRequest, env: Env) -> None:
        samples: list[model.Sample] = env.handle(
            command.SampleCrudCommand(
                user=env.get_root_user(),
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
            ),
            use_endpoint=False,
        )
        assert samples

        request.cls.all_samples = samples
        request.cls.test_samples = samples[:10]

    def test_retrieve_full_samples_by_ids(self, env: Env) -> None:
        sample_ids = [
            sample.id for sample in self.test_samples if sample.id is not None
        ]
        assert sample_ids

        full_samples: list[model.FullSample] = env.handle(
            command.RetrieveSamplesByIdCommand(
                user=env.get_root_user(),
                sample_ids=sample_ids,
            ),
            use_endpoint=False,
        )

        assert len(full_samples) == len(sample_ids)
        assert all(isinstance(sample, model.FullSample) for sample in full_samples)
        assert [x.sample.id for x in full_samples] == sample_ids

        full_sample_map = {x.sample.id: x for x in full_samples}

        for sample in self.test_samples[:2]:
            assert sample.id is not None
            assert full_sample_map[sample.id].sample.code == sample.code
            assert isinstance(full_sample_map[sample.id].read_sets, list)
            assert isinstance(full_sample_map[sample.id].seqs, list)

    def test_retrieve_full_samples_by_modified_range(self, env: Env) -> None:
        assert len(self.test_samples) >= 2

        first_sample = self.test_samples[0].model_copy()
        second_sample = self.test_samples[1]
        assert first_sample.id is not None
        assert second_sample.id is not None

        first_sample.code = first_sample.code + "_updated"

        updated_first_sample: model.Sample = env.handle(
            command.SampleCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.UPDATE_ONE,
                objs=first_sample,
            ),
            use_endpoint=False,
        )
        assert updated_first_sample.id is not None

        refreshed_samples: list[model.Sample] = env.handle(
            command.SampleCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_SOME,
                obj_ids=[updated_first_sample.id, second_sample.id],
            ),
            use_endpoint=False,
        )
        samples_by_id = {x.id: x for x in refreshed_samples}

        first_modified_at = samples_by_id[updated_first_sample.id].modified_at
        second_modified_at = second_sample.modified_at

        assert first_modified_at is not None
        assert second_modified_at is not None
        assert first_modified_at != second_modified_at

        target_start = first_modified_at - timedelta(seconds=1)
        target_end = first_modified_at + timedelta(seconds=1)

        query: model.SampleQuery = model.SampleQuery(
            label="seqdb_integration_test_query",
            modified_since=target_start,
            modified_until=target_end,
        )

        sample_query_result: model.SampleQueryResult = env.handle(
            command.RetrieveSamplesByQueryCommand(
                user=env.get_root_user(),
                sample_query=query,
            ),
            use_endpoint=False,
        )

        assert len(sample_query_result.sample_ids) == 1
        assert sample_query_result.sample_ids[0] == updated_first_sample.id
        assert sample_query_result.sample_query == query

    def test_retrieve_full_samples_with_duplicate_ids(self, env: Env) -> None:
        root_user = env.get_root_user()
        duplicate_sample_id = env.generate_id()

        with pytest.raises(ValueError, match="sample_ids must be unique"):
            env.handle(
                command.RetrieveSamplesByIdCommand(
                    user=root_user,
                    sample_ids=[duplicate_sample_id, duplicate_sample_id],
                ),
                use_endpoint=False,
            )

    def test_retrieve_sample_identifiers_by_ids(self, env: Env) -> None:
        sample_ids = [
            sample.id for sample in self.test_samples if sample.id is not None
        ]
        assert sample_ids

        identifiers: list[model.SampleIdentifier] = env.handle(
            command.RetrieveSampleIdentifiersByIdCommand(
                user=env.get_root_user(),
                sample_ids=sample_ids,
            ),
            use_endpoint=False,
        )

        assert isinstance(identifiers, list)
        assert all(isinstance(x, model.SampleIdentifier) for x in identifiers)
        returned_sample_ids = {x.internal_id for x in identifiers}
        assert returned_sample_ids.issubset(set(sample_ids))

    def test_retrieve_sample_identifiers_with_duplicate_ids(self, env: Env) -> None:
        duplicate_sample_id = env.generate_id()

        with pytest.raises(ValueError, match="sample_ids must be unique"):
            env.handle(
                command.RetrieveSampleIdentifiersByIdCommand(
                    user=env.get_root_user(),
                    sample_ids=[duplicate_sample_id, duplicate_sample_id],
                ),
                use_endpoint=False,
            )
