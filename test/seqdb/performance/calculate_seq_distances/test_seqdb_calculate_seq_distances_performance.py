import logging
from pathlib import Path
from test.seqdb.performance.calculate_seq_distances.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.performance.calculate_seq_distances.generate_seqdb_models import (
    generate_demo_seqdb_models,
)
from test.seqdb.performance.common import (
    create_dict_repository,
    set_service_repository,
    write_db_to_pickle,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.seqdb.seqdb_test_client import SeqGenerationSettings
from time import perf_counter
from typing import Any
from uuid import UUID

import pytest

from gen_epix.commondb.domain.enum import AppType, EtlStatus
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository

# Set to True to regenerate demo data, False to load from existing pickle file
CREATE_DEMO_DATA = True

N_SEQS_PER_BATCH = 100
DB_ENTRY_COUNTS: list[int] = [1]  # ]2, 10]

SEQ_SETTINGS = SeqGenerationSettings(n_loci=1000, locus_length=100)

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


def _build_upload_command(
    db: dict[type, dict[UUID, Any]],
    db_index: int,
    env: Env,
    settings: SeqGenerationSettings,
    seed: int | None = None,
) -> command.UploadSamplesCommand:
    """
    Given a created dict dataset, build a UploadSamplesCommand
    The id's from the db are extracted and used in generate_random_sequences()
    to create correctly linked objects for upload.
    db_index is used to select which set of objects to use for the command from the db.
    """
    protocols = list(db[model.Protocol].values())
    assembly_protocol_id = [
        protocol.id
        for protocol in protocols
        if protocol.protocol_type == enum.ProtocolType.ASSEMBLY
    ][db_index]
    locus_set_id = list(db[model.LocusSet].keys())[db_index]
    locus_detection_protocol_id = [
        protocol.id
        for protocol in protocols
        if protocol.protocol_type == enum.ProtocolType.SEQ_PROFILE
        and protocol.seq_profile_type == enum.SeqProfileType.ALLELE
    ][db_index]
    locus_code_map_id = list(db[model.LocusCodeMap].keys())[db_index]
    locus_ids = db[model.LocusSet][locus_set_id].locus_ids

    effective_settings = (
        settings if seed is None else settings.model_copy(update={"seed": seed})
    )
    sample_batch = env.generate_random_sequences(
        n_seqs=N_SEQS_PER_BATCH,
        settings=effective_settings,
        assembly_protocol_id=assembly_protocol_id,
        locus_set_id=locus_set_id,
        locus_detection_protocol_id=locus_detection_protocol_id,
        locus_code_map_id=locus_code_map_id,
        locus_ids=locus_ids,
    )
    return command.UploadSamplesCommand(
        sample_batch=sample_batch,
        user=env.get_root_user(),
    )


@pytest.mark.scenario_ids("TC-PERF-10-01")
class TestSampleBatchUploader:

    dbs: list[dict[type, dict[UUID, Any]]]
    repositories: list[SeqDictRepository]

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        """
        Configure root user for the test environment,
        if CREATE_DEMO_DATA is True, create datasets of varying sizes
        else load from existing pickle file, and create repositories based on the datasets
        """
        pickle_file = Path(__file__).parent / "test_sample_upload.pkl"

        # Configure root user
        user: model.User = env.retrieve_user_by_key("root1_1@org1.org")
        user.name = "root1_1"
        env.set_obj(user)
        env.set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )

        entities = env.app.domain.get_dag_sorted_entities(
            service_type=enum.ServiceType.SEQ,
            persistable=True,
        )

        if CREATE_DEMO_DATA:
            type(self).dbs = [
                generate_demo_seqdb_models(SEQ_SETTINGS.n_loci, n_to_create=count)
                for count in DB_ENTRY_COUNTS
            ]
            write_db_to_pickle(self.dbs[0], pickle_file)
            type(self).repositories = [
                create_dict_repository(pickle_file=None, db=db, entities=entities)
                for db in type(self).dbs
            ]
        else:
            assert pickle_file.exists()
            assert pickle_file.stat().st_size > 0
            type(self).repositories = [
                create_dict_repository(
                    pickle_file=pickle_file, db=None, entities=entities
                )
            ]

    @pytest.mark.parametrize(
        "dataset_idx", range(len(DB_ENTRY_COUNTS)), ids=DB_ENTRY_COUNTS
    )
    def test_sample_batch_for_upload_happy_flow(
        self, env: Env, dataset_idx: int
    ) -> None:

        set_service_repository(env, self.repositories[dataset_idx])

        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        n_entries = len(self.dbs[dataset_idx][model.LocusSet])
        commands_to_upload: list[command.UploadSamplesCommand] = [
            _build_upload_command(self.dbs[dataset_idx], i, env, SEQ_SETTINGS, seed=i)
            for i in range(n_entries)
        ]

        durations: list[float] = []
        for cmd in commands_to_upload:
            start = perf_counter()
            result: model.SampleBatchUploadResult = env.app.handle(cmd)
            durations.append(perf_counter() - start)
            assert result.get_status_count()[EtlStatus.FAILED] == 0
            assert result.get_status_count()[EtlStatus.PENDING] == 0
        total = sum(durations)
        avg = total / len(durations) if durations else 0.0

        print(f"\nUploadSamplesCommands={len(commands_to_upload)}")
        print(f"n_seqs_per_batch={N_SEQS_PER_BATCH}")
        print(f"total_time={total:.4f}s")
        print(f"avg_time_per_upload={avg:.4f}s\n")

        # profiler.stop()
        # profiler.write_html(
        #     "./test/output/profile_calculate_seq_distances.html"
        # )
