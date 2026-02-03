import base64
import hashlib
import logging
from pathlib import Path
from test.commondb.util import retrieve_db_data_from_file
from test.seqdb.performance.seq_distance.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.seqdb.seqdb_test_client import SeqGenerationSettings
from uuid import UUID

import pandas as pd
import pytest

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain import enum
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

    @staticmethod
    def convert_upload_to_profile(
        upload_profile: model.AlleleProfileForUpload,
    ) -> model.AlleleProfile:
        if not upload_profile.allele_ids:
            raise ValueError("allele_ids must be provided in AlleleProfileForUpload")

        sorted_allele_ids = sorted(
            upload_profile.allele_ids, key=lambda x: x or NULL_ID
        )
        allele_bytes_list = [
            (allele_id.bytes if allele_id else NULL_ID.bytes)
            for allele_id in sorted_allele_ids
        ]
        allele_profile_bytes = b"".join(allele_bytes_list)
        allele_profile_str = base64.b64encode(allele_profile_bytes).decode("ascii")

        sha256 = hashlib.sha256()
        sha256.update(allele_profile_bytes)
        allele_profile_hash = UUID(sha256.digest()[:16].hex())

        n_loci = sum(
            1 for allele_id in upload_profile.allele_ids if allele_id is not None
        )

        allele_profile = model.AlleleProfile(  # type: ignore[call-arg]
            sample_id=upload_profile.sample_id,
            seq_id=upload_profile.seq_id,
            locus_set_id=upload_profile.locus_set_id,
            locus_detection_protocol_id=upload_profile.locus_detection_protocol_id,
            n_loci=n_loci,
            allele_profile=allele_profile_str,
            allele_profile_format=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
            allele_profile_hash=allele_profile_hash,
        )

        return allele_profile

    def generate_allele_profiles(self, env: Env) -> list[model.AlleleProfile]:
        settings = SeqGenerationSettings(
            n_loci=5,
            locus_length=20,
            p_locus_deletion=0.01,
            p_nucleotide_substitution=0.02,
            p_nucleotide_deletion=0.005,
            seed=1001,
        )
        batch = SeqdbTestClient.generate_random_sequences(
            n_seqs=10,
            settings=settings,
        )

        allele_profiles: list[model.AlleleProfile] = []
        for sample in batch.samples:
            for allele_profile_for_upload in sample.allele_profiles:
                allele_profile = self.convert_upload_to_profile(
                    allele_profile_for_upload
                )
                allele_profiles.append(allele_profile)

        return allele_profiles

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

    def test_dummy(self, env: Env) -> None:
        users = env.app.handle(
            command.UserCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_ALL,
            )
        )
        print(users)
