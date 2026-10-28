from pathlib import Path
from typing import Any, ClassVar
from uuid import uuid4

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
from gen_epix.filter import (
    CompositeFilter,
    ContainsStringFilter,
    EqualsStringFilter,
    ExistsFilter,
    LogicalOperator,
    StringSetFilter,
)

pytestmark = pytest.mark.integration

Base: Any = declarative_base()


class LifecycleRow(Base):
    __tablename__ = "repository_lifecycle"
    __table_args__: ClassVar[tuple[Any, ...]] = tuple()

    id = sa.Column(sa.String(64), primary_key=True, nullable=False)
    value = sa.Column(sa.Integer, nullable=False)
    label = sa.Column(sa.String(128), nullable=True)


class LifecycleModel(Model):
    ENTITY: ClassVar[Entity] = Entity(
        persistable=True,
        id_field_name="id",
        table_name="repository_lifecycle",
    )

    id: str
    value: int
    label: str | None = None


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


def test_sql_server_inverted_filters_match_null_and_nonmatching_values() -> None:
    from gen_epix.casedb.domain import enum as casedb_enum
    from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
    from gen_epix.commondb.domain.util import get_app_cfgs
    from gen_epix.seqdb.domain import enum as seqdb_enum

    test_type = "FASTAPP_MSSQL_FILTER_INTEGRATION"
    seqdb_app_cfgs = get_app_cfgs(
        AppType.SEQDB,
        seqdb_enum.ServiceType,
        seqdb_enum.RepositoryType,
        test_type,
        dev_idp_config=DevIdpConfig.NONE,
        log_any=False,
    )
    casedb_app_cfgs = get_app_cfgs(
        AppType.CASEDB,
        casedb_enum.ServiceType,
        casedb_enum.RepositoryType,
        test_type,
        dev_idp_config=DevIdpConfig.NONE,
        seqdb_app_cfgs=seqdb_app_cfgs,
        log_any=False,
    )
    app_cfg = casedb_app_cfgs[f"{test_type}__{DevRepositoryConfig.SA_SQL.value}"]
    connection_string = app_cfg.cfg["repository"]["defaults"]["props"][
        "connection_string"
    ]
    connection_error = SARepository.test_connection(connection_string, timeout=5)
    if connection_error is not None:
        pytest.skip(
            "SQL Server integration unavailable: " f"{type(connection_error).__name__}"
        )

    repository = SARepository.create_repository(
        entities=[LifecycleModel.ENTITY],
        connection_string=connection_string,
        create_database_objects=True,
    )
    run_id = uuid4().hex
    null_id = f"{run_id}-null"
    matching_id = f"{run_id}-matching"
    nonmatching_id = f"{run_id}-nonmatching"
    try:
        repository.create_some(
            LifecycleModel,
            "test-user",
            [
                LifecycleModel(id=null_id, value=1, label=None),
                LifecycleModel(id=matching_id, value=2, label="matching"),
                LifecycleModel(id=nonmatching_id, value=3, label="other"),
            ],
        )
        filters_and_ids = [
            (ExistsFilter(key="label", invert=True), {null_id}),
            (
                EqualsStringFilter(key="label", value="matching", invert=True),
                {null_id, nonmatching_id},
            ),
            (
                StringSetFilter(
                    key="label", members=frozenset({"matching"}), invert=True
                ),
                {null_id, nonmatching_id},
            ),
            (
                ContainsStringFilter(key="label", value="match", invert=True),
                {null_id, nonmatching_id},
            ),
            (
                CompositeFilter(
                    operator=LogicalOperator.AND,
                    filters=[
                        EqualsStringFilter(key="label", value="matching"),
                        ExistsFilter(key="value"),
                    ],
                    invert=True,
                ),
                {null_id, nonmatching_id},
            ),
        ]

        for filter_, expected_ids in filters_and_ids:
            results = repository.read_all(LifecycleModel, filter_)
            assert {obj.id for obj in results} == expected_ids
    finally:
        repository._engine.dispose()  # type: ignore[attr-defined]  # pylint: disable=protected-access
        SARepository.clear_repository_content(
            entities=[LifecycleModel.ENTITY],
            connection_string=connection_string,
        )
