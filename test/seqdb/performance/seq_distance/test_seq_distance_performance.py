import base64
import hashlib
import logging
import uuid
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

    def generate_demo_data(
        self, env: Env, allele_profiles: list[model.AlleleProfile]
    ) -> tuple[list[UUID], UUID]:
        root_user = env.get_root_user()

        # allele_profiles = self.generate_allele_profiles(env)
        assert len(allele_profiles) > 1

        n_loci = allele_profiles[0].n_loci
        created_locus_set = env.app.handle(
            command.LocusSetCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.LocusSet(  # type: ignore[call-arg]
                    code="LS_TEST",
                    name="Locus Set Test",
                    n_loci=n_loci,
                    locus_ids=[uuid.uuid4() for _ in range(n_loci)],
                ),
            )
        )
        assert isinstance(created_locus_set, model.LocusSet)
        locus_set_id = created_locus_set.id
        assert locus_set_id is not None

        # Create a dummy LocusDetectionProtocol with matching id
        created_ldp = env.app.handle(
            command.LocusDetectionProtocolCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.LocusDetectionProtocol(  # type: ignore[call-arg]
                    code="LDP_TEST",
                    name="Locus Detection Protocol Test",
                    version="1.0",
                ),
            )
        )
        assert isinstance(created_ldp, model.LocusDetectionProtocol)
        locus_detection_protocol_id = created_ldp.id
        assert locus_detection_protocol_id is not None

        # Create a Sample linked to an existing DataCollection
        data_collections = env.app.handle(
            command.DataCollectionCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        assert isinstance(data_collections, list) and len(data_collections) > 0
        dc_id = data_collections[0].id  # type: ignore[attr-defined]
        assert dc_id is not None
        created_sample = env.app.handle(
            command.SampleCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Sample(  # type: ignore[call-arg]
                    code="SAMPLE_TEST",
                    created_in_data_collection_id=dc_id,
                ),
            )
        )
        assert isinstance(created_sample, model.Sample)
        sample_id = created_sample.id
        assert sample_id is not None

        # Assign the created IDs to all allele profiles to satisfy link checks
        for ap in allele_profiles:
            ap.sample_id = sample_id  # type: ignore[assignment]
            ap.locus_set_id = locus_set_id  # type: ignore[assignment]
            ap.locus_detection_protocol_id = locus_detection_protocol_id  # type: ignore[assignment]
            ap.seq_id = None  # avoid invalid Seq linkage for this happy-flow

        # 3) Create an allele-based distance protocol for the locus set
        created_protocol = env.app.handle(
            command.SeqDistanceProtocolCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.SeqDistanceProtocol(  # type: ignore[call-arg]
                    code="ALLELE_HAMMING_TEST",
                    name="Allele Hamming Test",
                    version="1.0",
                    is_integer_distance=True,
                    seq_distance_protocol_type=enum.SeqDistanceProtocolType.ALLELE_HAMMING,
                    locus_set_id=locus_set_id,
                    max_stored_distance=1e6,  # large threshold to store all distances
                ),
            )
        )
        assert isinstance(created_protocol, model.SeqDistanceProtocol)
        protocol_id = created_protocol.id
        assert protocol_id is not None

        # 4) Persist allele profiles
        created_profiles = env.app.handle(
            command.AlleleProfileCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_SOME,
                objs=allele_profiles,
            )
        )
        assert isinstance(created_profiles, list)
        profile_ids: list[UUID] = [p.id for p in created_profiles if p.id is not None]  # type: ignore[attr-defined]
        assert len(profile_ids) == len(allele_profiles)

        # 5) Compute distance matrix from allele profiles
        dist_matrix = SeqdbTestClient.calculate_distance_matrix_from_allele_profile(
            created_profiles  # type: ignore[arg-type]
        )
        assert dist_matrix.matrix.shape[0] == len(profile_ids)

        # 6) Persist SeqDistance records per profile using the matrix
        seq_distances: list[model.SeqDistance] = []
        n = len(profile_ids)
        for i in range(n):
            # Build {other_profile_id_str: distance} mapping including self with 0
            distances_dict: dict[str, float] = {}
            for j in range(n):
                pid_j = profile_ids[j]
                distances_dict[str(pid_j)] = float(dist_matrix.matrix[i][j])
            seq_distance = model.SeqDistance(  # type: ignore[call-arg]
                sample_id=sample_id,
                seq_id=created_profiles[i].seq_id,  # type: ignore[attr-defined]
                seq_distance_protocol_id=protocol_id,
                profile_id=profile_ids[i],
                distance_format=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
                distances=pd.Series(distances_dict).to_json(),
            )
            seq_distances.append(seq_distance)

        persisted = env.app.handle(
            command.SeqDistanceCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_SOME,
                objs=seq_distances,
            )
        )
        assert isinstance(persisted, list)

        return profile_ids, protocol_id


class TestSeqDistancePerformance(SeqDistancePerformanceSetup):

    def test_dummy(self, env: Env) -> None:
        users = env.app.handle(
            command.UserCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_ALL,
            )
        )

    def test_get_similar_profiles_happy_flow(self, env: Env) -> None:
        root_user = env.get_root_user()

        profile_ids, protocol_id = self.generate_demo_data(
            env, self.generate_allele_profiles(env)
        )

        first_profile_id = profile_ids[0]
        result_ids = env.app.handle(
            command.GetSimilarProfilesCommand(
                user=root_user,
                seq_distance_protocol_id=protocol_id,
                profile_ids=profile_ids,
                max_distance=1.0,  # allow close matches
            )
        )
        assert isinstance(result_ids, list)
        # Should at least include the first profile itself (distance 0)
        assert str(first_profile_id) in set(result_ids) or first_profile_id in set(
            result_ids
        )
        # And should include more than one match when querying multiple profiles
        assert len(result_ids) > 1
