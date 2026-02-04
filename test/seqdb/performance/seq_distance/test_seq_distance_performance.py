import logging
from pathlib import Path
from test.commondb.util import retrieve_db_data_from_file
from test.seqdb.performance.seq_distance.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.performance.seq_distance.generate_demo_seq_distances import (
    generate_allele_profiles,
    generate_demo_data,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from uuid import UUID

import pandas as pd
import pytest

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=SEQDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class SeqDistancePerformanceSetup:
    ORDERED_MODEL_TO_SHEET_MAP: dict[type[model.Model], str] = {
        model.Organization: "Organization",
        model.DataCollection: "DataCollection",
        model.User: "User",
        # TODO: Add more below as needed
    }

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        self.excel_file = Path(__file__).parent / "test_seq_distance_performance.xlsx"
        self.pickle_file = Path(__file__).parent / "test_seq_distance_performance.pkl"
        self.case_crud_commands: pd.DataFrame | None = None
        self.retrieve_data_from_file(env)

    def retrieve_data_from_file(self, env: Env) -> None:
        retrieve_db_data_from_file(
            test_client=env,
            ordered_model_to_sheet_map=self.ORDERED_MODEL_TO_SHEET_MAP,
            excel_file=self.excel_file,
            pickle_file=self.pickle_file,
            extra_table_to_sheet_map={},
        )


class TestSeqDistancePerformance(SeqDistancePerformanceSetup):


    def test_get_similar_profiles_happy_flow(self, env: Env) -> None:
        profile_ids, protocol_id = generate_demo_data(env, generate_allele_profiles())
        result_ids: list[UUID] = env.app.handle(
            command.GetSimilarProfilesCommand(
                user=env.get_root_user(),
                seq_distance_protocol_id=protocol_id,
                profile_ids=[profile_ids[0]],
                max_distance=1.0,
            )
        )
        assert isinstance(result_ids, list)
        assert str(profile_ids[0]) in set(result_ids) or profile_ids[0] in set(
            result_ids
        )
        assert len(result_ids) > 1
