import logging
from pathlib import Path
from test.seqdb.integration.sample_batch_uploader.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.integration.sample_batch_uploader.create_demo_data import (
    generate_demo_seqdb_models,
)
from test.seqdb.performance.seq_distance.test_seq_distance_performance import (
    create_dict_repository,
    write_db_to_pickle,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.seqdb.seqdb_test_client import SeqGenerationSettings
from typing import Any
from uuid import UUID

import pytest

from gen_epix.commondb.domain.enum import AppType, UploadStatus
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository

# Set to True to regenerate demo data, False to load from existing pickle file
CREATE_DEMO_DATA: bool = True

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
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


class SampleBatchUploaderSetUp:

    db: dict[type, dict[UUID, Any]]

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        self.pickle_file = Path(__file__).parent / "test_sample_batch_uploader.pkl"
        self.create_user_first_root(env)
        self.setup_demo_data(env)

    def create_user_first_root(self, env: Env) -> None:
        user: model.User = env.retrieve_user_by_key("root1_1@org1.org")
        user.name = "root1_1"
        env._set_obj(user)
        env._set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )

    def setup_demo_data(self, env: Env) -> None:
        """
        Method to either create or load a demo sample batch for upload,
        which can be used for testing the sample batch uploader.

        If CREATE_DEMO_DATA is True, generates new demo data and writes to pickle.
        If CREATE_DEMO_DATA is False, loads existing data from pickle file.
        """
        entities = env.app.domain.get_dag_sorted_entities(
            service_type=enum.ServiceType.SEQ,
            persistable=True,
        )

        seq_dict_repository: SeqDictRepository
        if CREATE_DEMO_DATA:
            # Create new demo data
            type(self).db = generate_demo_seqdb_models()
            write_db_to_pickle(self.db, self.pickle_file)
            seq_dict_repository = create_dict_repository(
                pickle_file=None,
                db=type(self).db,
                entities=entities,
            )
        else:
            assert self.pickle_file.exists()
            assert self.pickle_file.stat().st_size > 0

            # Create repository from pickle file
            seq_dict_repository = create_dict_repository(
                pickle_file=self.pickle_file,
                db=None,
                entities=entities,
            )

        # Replace the repository in the service
        app = env.app.impl.services[enum.ServiceType.SEQ].app
        seq_service = app.impl.services[enum.ServiceType.SEQ]
        seq_service.repository = seq_dict_repository


class TestSampleBatchUploader(SampleBatchUploaderSetUp):

    SETTINGS: SeqGenerationSettings = SeqGenerationSettings(
        n_loci=5,
        locus_length=100,
    )

    def test_sample_batch_for_upload_happy_flow(self, env: Env) -> None:

        assembly_protocol_id = next(iter(self.db[model.AssemblyProtocol].keys()))
        locus_set_id = next(iter(self.db[model.LocusSet].keys()))
        locus_detection_protocol_id = next(
            iter(self.db[model.LocusDetectionProtocol].keys())
        )

        sample_batch_for_upload = env.generate_random_sequences(
            n_seqs=10,
            settings=self.SETTINGS,
            assembly_protocol_id=assembly_protocol_id,
            locus_set_id=locus_set_id,
            locus_detection_protocol_id=locus_detection_protocol_id,
        )

        cmd = command.UploadSamplesCommand(
            sample_batch=sample_batch_for_upload,
            user=env.get_root_user(),
        )
        sample_batch_upload_result: model.SampleBatchUploadResult = env.app.handle(cmd)

        assert len(sample_batch_upload_result.samples) == len(
            sample_batch_for_upload.samples
        )

        for i, _ in enumerate(sample_batch_for_upload.samples):
            assert (
                sample_batch_upload_result.samples[i].allele_profiles[0].status  # type: ignore[index]
                == UploadStatus.CREATED
            )
