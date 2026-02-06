import logging
import pickle
from pathlib import Path
from test.seqdb.performance.create_demo_seq_distances import (
    create_seq_distance_database,
)
from test.seqdb.performance.seq_distance.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from uuid import UUID

import pytest

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain import DOMAIN
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

CREATE_DEMO_DATA: bool = True


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
    empty_sa_sqlite_file: Path, entities: list[Entity]
) -> SeqSARepository:
    service_type = seqdb_enum.ServiceType.SEQ
    return SeqSARepository.create_repository(  # type: ignore[return-value]
        entities=entities,
        file=empty_sa_sqlite_file,
        name=service_type.value,
        recreate_sqlite_file=True,
    )


def fill_empty_sqlite_repository(
    dict_repository: SeqDictRepository,
    sqlite_repository: SeqSARepository,
    entities: list[Entity],
    user_id: UUID,
) -> None:
    for entity in entities:
        model_class = entity.model_class
        objs: list[model.Model] = dict_repository.crud(  # type: ignore[assignment]
            dict_repository.uow(),
            user_id,
            model_class,
            None,
            None,
            CrudOperation.READ_ALL,
            return_copy=False,
        )
        sqlite_repository.crud(
            sqlite_repository.uow(),
            user_id,
            model_class,
            objs,
            None,
            CrudOperation.CREATE_SOME,
        )


class SeqDistancePerformanceSetup:

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:

        if CREATE_DEMO_DATA:

            self.create_demo_data(env)
        else:
            # load demo data ...
            pass

    def create_demo_data(self, env: Env) -> None:
        # TODO: If this method is correctly implemented, it can be refactored to create 100, 200 and 500 seq distances
        db_100 = create_seq_distance_database(
            env,
            n_loci=10,
            n_seqs=10,
        )
        entities: list[Entity] = [model_class.ENTITY for model_class in db_100.keys()]  # type: ignore[attr-defined]
        dag_sorted_entities = DOMAIN.get_dag_sorted_entities(service_type=seqdb_enum.ServiceType.SEQ, persistable=True)
        # use dag sorted entities to ensure correct order of creation in sqlite repository
        entities = [entity for entity in dag_sorted_entities if entity in entities]

        write_db_to_pickle(
            db_100, Path(__file__).parent / "test_seq_distance_performance_100.pkl"
        )
        dict_repository_100 = create_dict_repository(
            db=db_100, pickle_file=None, entities=entities
        )
        sa_repository_100 = create_sqlite_repository(
            Path(__file__).parent / "test_seq_distance_performance_100.sqlite",
            entities,
        )

        fill_empty_sqlite_repository(
            dict_repository_100,
            sa_repository_100,
            entities,
            env.get_root_user().id,  # type: ignore[arg-type]
        )
        print('Demo data created and saved to pickle and sqlite files')


class TestSeqDistancePerformance(SeqDistancePerformanceSetup):

    def test_get_similar_profiles_happy_flow(self, env: Env) -> None:

        profiles: list[model.AlleleProfile] = env.app.handle(
            command.AlleleProfileCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_ALL,
            )
        )
        profile_ids = [x.id for x in profiles if x.id is not None]
        seq_distance_protocols: list[model.SeqDistanceProtocol] = env.app.handle(
            command.SeqDistanceProtocolCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_ALL,
            )
        )
        assert len(seq_distance_protocols) == 1
        protocol_id = seq_distance_protocols[0].id
        result_ids: list[UUID] = env.app.handle(
            command.GetSimilarProfilesCommand(
                user=env.get_root_user(),
                seq_distance_protocol_id=protocol_id,
                profile_ids=profile_ids,
                max_distance=1.0,
            )
        )
        assert isinstance(result_ids, list)
        assert profile_ids[0] in result_ids
        assert len(result_ids) > 1
