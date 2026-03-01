import logging
import pickle
from pathlib import Path
from test.seqdb.performance.create_demo_seq_distances import (
    create_seq_distance_database,
)
from test.seqdb.performance.seq_distance.base import (
    DEV_REPOSITORY_CONFIG,
    ENTITIES,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from time import perf_counter
from uuid import UUID

import pytest
from pydantic import BaseModel

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository
from gen_epix.seqdb.repositories.seq_sa import SeqSARepository

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)

CREATE_DEMO_DATA: bool = False
BASE = Path(__file__).parent
DATASETS: list[tuple[int, Path, Path]] = [
    (
        100,
        BASE / "test_seq_distance_performance_100.pkl",
        BASE / "test_seq_distance_performance_100.sqlite",
    ),
    (
        200,
        BASE / "test_seq_distance_performance_200.pkl",
        BASE / "test_seq_distance_performance_200.sqlite",
    ),
    (
        500,
        BASE / "test_seq_distance_performance_500.pkl",
        BASE / "test_seq_distance_performance_500.sqlite",
    ),
]


class TestRepositoryPerformance(BaseModel):

    model_config = {"arbitrary_types_allowed": True}

    repository_type: seqdb_enum.RepositoryType
    dataset_size: int
    file: Path
    repository: SeqDictRepository | SeqSARepository


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=SEQDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


def write_db_to_pickle(
    db: dict[type, dict[UUID, model.Model]], pickle_file: Path
) -> None:
    with open(pickle_file, "wb") as f:
        pickle.dump(db, f)


# def get_filtered_entities(
#     db: dict[type, dict[UUID, model.Model]],
# ) -> list[Entity]:
#     entities: list[Entity] = [model_class.ENTITY for model_class in db.keys()]  # type: ignore[attr-defined]
#     dag_entities = DOMAIN.get_dag_sorted_entities(
#         service_type=seqdb_enum.ServiceType.SEQ, persistable=True
#     )
#     entities = [entity for entity in dag_entities if entity in entities]
#     return entities


def create_dict_repository(
    pickle_file: Path | None,
    db: dict[type, dict[UUID, model.Model]] | None,
    entities: list[Entity],
) -> SeqDictRepository:

    if pickle_file is not None:
        with open(pickle_file, "rb") as f:
            db = pickle.load(f)

    return SeqDictRepository(entities=entities, db=db)  # type: ignore[arg-type]


def create_sqlite_repository(
    empty_sa_sqlite_file: Path,
    entities: list[Entity],
    recreate_sqlite_file: bool = True,
) -> SeqSARepository:
    service_type = seqdb_enum.ServiceType.SEQ
    return SeqSARepository.create_repository(  # type: ignore[return-value]
        entities=entities,
        file=empty_sa_sqlite_file,
        name=service_type.value,
        recreate_sqlite_file=recreate_sqlite_file,
    )


def fill_empty_sqlite_repository(
    dict_repository: SeqDictRepository,
    sqlite_repository: SeqSARepository,
    entities: list[Entity],
    user_id: UUID,
) -> None:
    with (
        dict_repository.uow() as dict_uow,
        sqlite_repository.uow() as sa_uow,
    ):
        for entity in entities:
            model_class = entity.model_class
            objs: list[model.Model] = dict_repository.crud(  # type: ignore[assignment]
                dict_uow,
                user_id,
                model_class,
                None,
                None,
                CrudOperation.READ_ALL,
                return_copy=False,
            )
            sqlite_repository.crud(
                sa_uow,
                user_id,
                model_class,
                objs,
                None,
                CrudOperation.CREATE_SOME,
            )


def ensure_datasets_exist_and_valid() -> None:
    for _, pkl_path, sqlite_path in DATASETS:
        assert (
            pkl_path.exists() and pkl_path.stat().st_size > 0
        ), f"Pickle file {pkl_path} missing or empty"
        assert (
            sqlite_path.exists() and sqlite_path.stat().st_size > 0
        ), f"SQLite file {sqlite_path} missing or empty"


class BaseSeqDistancePerformance:

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:

        if CREATE_DEMO_DATA:

            self.create_demo_data(env)
        else:
            ensure_datasets_exist_and_valid()

    def create_demo_data(self, env: Env) -> None:

        def create_and_persist(
            env: Env, n_seqs: int, pickle_path: Path, sqlite_path: Path
        ) -> None:
            db = create_seq_distance_database(n_loci=10, n_seqs=n_seqs)
            write_db_to_pickle(db, pickle_path)
            dict_repo = create_dict_repository(
                db=db, pickle_file=None, entities=ENTITIES
            )
            sa_repo = create_sqlite_repository(
                sqlite_path, ENTITIES, recreate_sqlite_file=True
            )
            fill_empty_sqlite_repository(
                dict_repo, sa_repo, ENTITIES, env.get_root_user().id  # type: ignore[arg-type]
            )

        for n_seqs, pkl, sqlite in DATASETS:
            create_and_persist(env, n_seqs, pkl, sqlite)
        print("Demo data for 100, 200, 500 created and persisted")


class TestSeqDistancePerformance(BaseSeqDistancePerformance):

    dict_repositories: list[TestRepositoryPerformance] = []
    sa_repositories: list[TestRepositoryPerformance] = []

    @pytest.fixture(scope="class", autouse=True)
    def setup_repositories(self) -> None:
        """
        Method that initializes the repositories for the tests.
        The method reads in the datasets from the DATASETS list,
        creates two separate LISTS with TestRepositoryPerformance for each dataset
        and sets them as CLASS VARIABLES to be used in the parameterized tests.
        """
        # self.dict_repositories: list[TestRepositoryPerformance] = []
        # self.sa_repositories: list[TestRepositoryPerformance] = []
        # self.repositories: list[TestRepositoryPerformance] = []
        for size, pkl_path, sqlite_path in DATASETS:
            dict_repo = create_dict_repository(
                db=None, pickle_file=pkl_path, entities=ENTITIES
            )
            sa_repo = create_sqlite_repository(
                sqlite_path, ENTITIES, recreate_sqlite_file=False
            )
            self.dict_repositories.append(
                TestRepositoryPerformance(
                    repository_type=seqdb_enum.RepositoryType.DICT,
                    dataset_size=size,
                    file=pkl_path,
                    repository=dict_repo,
                )
            )
            self.sa_repositories.append(
                TestRepositoryPerformance(
                    repository_type=seqdb_enum.RepositoryType.SA_SQLITE,
                    dataset_size=size,
                    file=sqlite_path,
                    repository=sa_repo,
                )
            )

    @pytest.mark.parametrize(
        "repository_type",
        [seqdb_enum.RepositoryType.DICT, seqdb_enum.RepositoryType.SA_SQLITE],
    )
    def test_retrieve_similar_profiles_happy_flow(
        self, env: Env, repository_type: seqdb_enum.RepositoryType
    ) -> None:
        test_repositories_performance: list[TestRepositoryPerformance]
        if repository_type == seqdb_enum.RepositoryType.DICT:
            test_repositories_performance = self.dict_repositories
        elif repository_type == seqdb_enum.RepositoryType.SA_SQLITE:
            test_repositories_performance = self.sa_repositories

        for test_repository_performance in test_repositories_performance:
            with test_repository_performance.repository.uow() as uow:
                profiles: list[model.AlleleProfile] = (
                    test_repository_performance.repository.crud(  # type: ignore[assignment]
                        uow,
                        env.get_root_user().id,
                        model.AlleleProfile,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                    )
                )
                profile_ids: list[UUID] = [x.id for x in profiles if x.id is not None]
                protocols: list[model.SeqDistanceProtocol] = (
                    test_repository_performance.repository.crud(  # type: ignore[assignment]
                        uow,
                        env.get_root_user().id,
                        model.SeqDistanceProtocol,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                    )
                )
                assert len(protocols) == 1
                protocol_id = protocols[0].id
            start = perf_counter()
            with test_repository_performance.repository.uow() as uow:
                result_ids = (
                    test_repository_performance.repository.retrieve_similar_profiles(
                        uow,
                        protocol_id,  # type: ignore[arg-type]
                        profile_ids,
                        5.0,
                    )
                )
            duration = perf_counter() - start
            assert isinstance(result_ids, list)
            expected_id = profile_ids[0]
            assert (expected_id in result_ids) or (str(expected_id) in result_ids)
            assert len(result_ids) > 1
            print(
                f"\n{test_repository_performance.repository_type} size={test_repository_performance.dataset_size} duration={duration:.4f}s"
            )
