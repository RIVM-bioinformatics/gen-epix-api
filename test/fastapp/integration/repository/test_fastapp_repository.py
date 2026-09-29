from pathlib import Path
from typing import Any, ClassVar

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository
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
