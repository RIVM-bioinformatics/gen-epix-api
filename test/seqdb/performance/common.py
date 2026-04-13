import pickle
from pathlib import Path
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from uuid import UUID

from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository
from gen_epix.seqdb.repositories.seq_sa import SeqSARepository


def write_db_to_pickle(
    db: dict[type, dict[UUID, model.Model]], pickle_file: Path
) -> None:
    with open(pickle_file, "wb") as f:
        pickle.dump(db, f)


def create_dict_repository(
    pickle_file: Path | None,
    db: dict[type, dict[UUID, model.Model]] | None,
    entities: list[Entity],
    missing_data: str = "ignore",
) -> SeqDictRepository:

    if pickle_file is not None:
        with open(pickle_file, "rb") as f:
            db = pickle.load(f)

    return SeqDictRepository(
        entities=entities,
        db=db,
        missing_data=missing_data,
    )  # type: ignore[arg-type]


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
                CrudOperation.READ_ALL,
                return_copy=False,
            )
            sqlite_repository.crud(
                sa_uow,
                user_id,
                model_class,
                CrudOperation.CREATE_SOME,
                objs=objs,
            )


def set_service_repository(env: Env, repository: SeqDictRepository) -> None:
    """Point the live SEQ service at the given repository."""
    app = env.app.impl.services[enum.ServiceType.SEQ].app
    app.impl.services[enum.ServiceType.SEQ].repository = repository
    app.impl.services[enum.ServiceType.SEQ].repository = repository
