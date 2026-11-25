import os
from pathlib import Path
from typing import Any, ClassVar, cast

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, IsolationLevel
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.repository import BaseRepository

pytestmark = pytest.mark.integration

Base: Any = declarative_base()


class LifecycleRow(Base):
    __tablename__ = "repository_lifecycle"
    __table_args__: ClassVar[tuple[Any, ...]] = tuple()

    id = sa.Column(sa.String, primary_key=True, nullable=False)
    value = sa.Column(sa.Integer, nullable=False)


class LifecycleModel(Model):
    ENTITY: ClassVar[Entity] = Entity(
        persistable=True,
        id_field_name="id",
        table_name="repository_lifecycle",
    )

    id: str
    value: int


LifecycleModel.ENTITY.set_model_class(LifecycleModel)
LifecycleModel.ENTITY.set_db_model_class(LifecycleRow)


def test_mssql_read_committed_uow() -> None:
    """Check the SQL Server isolation level on the active transaction."""
    url = os.environ.get("FASTAPP_MSSQL_TEST_URL")
    if not url:
        pytest.skip("Set FASTAPP_MSSQL_TEST_URL to run against SQL Server")

    engine = sa.create_engine(url)
    try:
        repository = SARepository(engine, register_mappers=False)
        with repository.uow(isolation_level=IsolationLevel.READ_COMMITTED) as uow:
            session = cast(SAUnitOfWork, uow).session
            actual_level = session.scalar(
                sa.text(
                    "SELECT transaction_isolation_level FROM sys.dm_exec_sessions "
                    "WHERE session_id = @@SPID"
                )
            )
            assert actual_level == 2
    finally:
        engine.dispose()


@pytest.mark.parametrize("repository_class", [DictRepository, SARepository])
def test_repository_lifecycle(
    repository_class: type[BaseRepository], tmp_path: Path
) -> None:
    entities = [LifecycleModel.ENTITY]
    connection_string: str | None = None
    if repository_class is SARepository:
        sqlite_file = tmp_path / "repository_lifecycle.sqlite"
        connection_string = f"sqlite:///{sqlite_file.as_posix()}"
        repository = repository_class.create_repository(
            entities=entities,
            connection_string=connection_string,
            recreate_sqlite_file=True,
        )
    else:
        repository = repository_class.create_repository(entities=entities)

    with repository.uow() as uow:
        created_ids = repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.CREATE_SOME,
            objs=[
                LifecycleModel(id="one", value=1),
                LifecycleModel(id="two", value=2),
            ],
            return_id=True,
        )
        assert created_ids == ["one", "two"]

        with pytest.raises(exc.DuplicateIdsError):
            repository.crud(
                uow,
                "user",
                LifecycleModel,
                CrudOperation.UPDATE_SOME,
                objs=[
                    LifecycleModel(id="one", value=10),
                    LifecycleModel(id="one", value=11),
                ],
            )

        read_objs = repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.READ_SOME,
            obj_ids=["two", "one"],
        )
        assert [obj.id for obj in read_objs] == ["two", "one"]

        updated_obj = repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.UPDATE_ONE,
            objs=LifecycleModel(id="one", value=10),
        )
        assert updated_obj.value == 10

        upserted_objs = repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.UPSERT_SOME,
            objs=[
                LifecycleModel(id="one", value=11),
                LifecycleModel(id="three", value=3),
            ],
        )
        assert [(obj.id, obj.value) for obj in upserted_objs] == [
            ("one", 11),
            ("three", 3),
        ]

        assert (
            len(
                repository.crud(
                    uow,
                    "user",
                    LifecycleModel,
                    CrudOperation.READ_ALL,
                    offset=1,
                )
            )
            == 2
        )
        assert repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.EXISTS_SOME,
            obj_ids=["one", "missing"],
        ) == [True, False]
        assert (
            repository.crud(
                uow,
                "user",
                LifecycleModel,
                CrudOperation.DELETE_ONE,
                obj_ids="two",
            )
            == "two"
        )
        assert set(
            repository.crud(
                uow,
                "user",
                LifecycleModel,
                CrudOperation.DELETE_ALL,
                return_id=True,
            )
        ) == {"one", "three"}

    with repository.uow() as uow:
        assert (
            repository.crud(
                uow,
                "user",
                LifecycleModel,
                CrudOperation.READ_ALL,
            )
            == []
        )

    if repository_class is SARepository:
        assert connection_string is not None
        repository._engine.dispose()  # type: ignore[attr-defined]  # pylint: disable=protected-access
        repository_class.clear_repository_content(
            entities=entities, connection_string=connection_string
        )
        engine = sa.create_engine(connection_string)
        try:
            assert "repository_lifecycle" not in sa.inspect(engine).get_table_names()
        finally:
            engine.dispose()
    else:
        repository_class.clear_repository_content(entities=entities)


@pytest.mark.parametrize("repository_class", [DictRepository, SARepository])
def test_delete_all_in_batches_returns_counts(
    repository_class: type[BaseRepository], tmp_path: Path
) -> None:
    """Delete in limited batches with the same counts and results in all backends."""
    entities = [LifecycleModel.ENTITY]
    if repository_class is SARepository:
        sqlite_file = tmp_path / "repository_delete_all_batches.sqlite"
        repository = repository_class.create_repository(
            entities=entities,
            connection_string=f"sqlite:///{sqlite_file.as_posix()}",
            recreate_sqlite_file=True,
        )
    else:
        repository = repository_class.create_repository(entities=entities)

    def delete_all(**kwargs: Any) -> Any:
        with repository.uow() as uow:
            return repository.crud(
                uow, "user", LifecycleModel, CrudOperation.DELETE_ALL, **kwargs
            )

    def read_ids() -> set[str]:
        with repository.uow() as uow:
            return {
                obj.id
                for obj in repository.crud(
                    uow, "user", LifecycleModel, CrudOperation.READ_ALL
                )
            }

    with repository.uow() as uow:
        repository.crud(
            uow,
            "user",
            LifecycleModel,
            CrudOperation.CREATE_SOME,
            objs=[LifecycleModel(id=f"id{i}", value=i) for i in range(5)],
        )

    # A limited batch deletes at most limit rows and reports their number
    assert delete_all(limit=2, return_count=True) == 2
    assert len(read_ids()) == 3
    # Ids of a limited batch are those that were deleted
    batch_ids = delete_all(limit=1, return_id=True)
    assert len(batch_ids) == 1
    assert len(read_ids()) == 2
    assert not read_ids() & set(batch_ids)
    # Without limit everything left is deleted and counted
    assert delete_all(return_count=True) == 2
    assert read_ids() == set()
    # Nothing left
    assert delete_all(limit=3, return_count=True) == 0
    # Without return flags nothing is returned
    assert delete_all(limit=3) is None
