from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, ClassVar, cast

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session, declarative_base

import gen_epix.fastapp.exc as exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, IsolationLevel
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import SAMapper
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.filter import (
    CompositeFilter,
    EqualsNumberFilter,
    EqualsStringFilter,
    LogicalOperator,
)

Base: Any = declarative_base()


class SARepoModel(Base):
    __tablename__ = "repo_model"
    __table_args__: ClassVar[tuple[Any, ...]] = tuple()
    id = sa.Column(sa.String, primary_key=True, nullable=False)
    value = sa.Column(sa.Integer, nullable=False)
    label = sa.Column(sa.String, nullable=True)


class RepoModel(Model):
    ENTITY: ClassVar[Entity] = Entity(
        persistable=True,
        id_field_name="id",
        table_name="repo_model",
    )
    id: str | None = None
    value: int
    label: str | None = None


RepoModel.ENTITY.set_model_class(RepoModel)
RepoModel.ENTITY.set_db_model_class(SARepoModel)


class OtherModel(Model):
    ENTITY: ClassVar[Entity] = Entity(
        persistable=True,
        id_field_name="id",
        table_name="other_model",
    )
    id: str | None = None
    value: int


def _make_obj(idx: int, *, value: int | None = None) -> RepoModel:
    return RepoModel(
        id=f"id-{idx}", value=idx if value is None else value, label=f"l-{idx}"
    )


@pytest.fixture
def repo() -> SARepository:
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = SARepository(
        engine,
        id="repo-id",
        name="repo-name",
        register_mappers=False,
    )
    repository.register_mapper(SAMapper(RepoModel, SARepoModel))
    return repository


def test_repository_properties_and_session(repo: SARepository) -> None:
    assert repo.id == "repo-id"
    assert repo.name == "repo-name"
    assert repo.default_isolation_level == IsolationLevel.SERIALIZABLE

    repo.default_isolation_level = IsolationLevel.READ_COMMITED
    assert repo.default_isolation_level == IsolationLevel.READ_COMMITED

    session = repo.get_session(expire_on_commit=True)
    assert isinstance(session, Session)
    session.close()


def test_uow_nested_and_invalid_nested_kwargs(repo: SARepository) -> None:
    with repo.uow() as outer_uow:
        nested_uow = repo.uow()
        assert isinstance(nested_uow, SAUnitOfWork)
        assert nested_uow.session is cast(SAUnitOfWork, outer_uow).session
        with pytest.raises(exc.RepositoryServiceError, match="b78b8c87"):
            repo.uow(invalid=True)


def test_register_get_mapper_and_duplicate_errors(repo: SARepository) -> None:
    mapper = repo.get_mapper(RepoModel)
    assert mapper.model_class is RepoModel

    with pytest.raises(exc.RepositoryInitializationServiceError, match="bd89986f"):
        repo.register_mapper(SAMapper(RepoModel, SARepoModel))

    with pytest.raises(exc.RepositoryInitializationServiceError, match="b8bd9844"):
        repo.get_mapper(OtherModel)


def test_register_mappers_with_entity(repo: SARepository) -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = SARepository(engine, register_mappers=False)
    repository.register_mappers(entities=[RepoModel.ENTITY])
    mapper = repository.get_mapper(RepoModel)
    assert mapper.model_class is RepoModel


def test_to_sql_and_from_sql(repo: SARepository) -> None:
    obj = _make_obj(1)
    row = repo.to_sql("user", RepoModel, obj)
    converted = repo.from_sql(RepoModel, row)
    assert converted == obj

    objs = [_make_obj(2), _make_obj(3)]
    rows = repo.to_sql("user", RepoModel, objs)
    converted_many = repo.from_sql(RepoModel, rows)
    assert converted_many == objs


def test_crud_input_validation_errors(repo: SARepository) -> None:
    with pytest.raises(exc.RepositoryServiceError, match="ff17823b"):
        repo.crud(
            cast(Any, object()),
            "user",
            RepoModel,
            CrudOperation.READ_ALL,
        )

    with repo.uow() as uow:
        with pytest.raises(exc.RepositoryServiceError, match="d9c8e5b3"):
            repo.crud(uow, "user", RepoModel, CrudOperation.READ_ALL, limit=-1)
        with pytest.raises(exc.RepositoryServiceError, match="a4f1c9d2"):
            repo.crud(uow, "user", RepoModel, CrudOperation.READ_ALL, offset=-1)


@pytest.mark.parametrize(
    "operation, method_name, kwargs",
    [
        (CrudOperation.CREATE_ONE, "create_one", {"objs": _make_obj(1)}),
        (CrudOperation.CREATE_SOME, "create_some", {"objs": [_make_obj(1)]}),
        (CrudOperation.READ_ONE, "read_one", {"obj_ids": "id-1"}),
        (CrudOperation.READ_SOME, "read_some", {"obj_ids": ["id-1"]}),
        (CrudOperation.READ_ALL, "read_all", {}),
        (CrudOperation.UPDATE_ONE, "update_one", {"objs": _make_obj(1)}),
        (CrudOperation.UPDATE_SOME, "update_some", {"objs": [_make_obj(1)]}),
        (CrudOperation.UPSERT_ONE, "upsert_one", {"objs": _make_obj(1)}),
        (CrudOperation.UPSERT_SOME, "upsert_some", {"objs": [_make_obj(1)]}),
        (CrudOperation.DELETE_ONE, "delete_one", {"obj_ids": "id-1"}),
        (CrudOperation.DELETE_SOME, "delete_some", {"obj_ids": ["id-1"]}),
        (CrudOperation.DELETE_ALL, "delete_all", {}),
        (CrudOperation.EXISTS_ONE, "exists_one", {"obj_ids": "id-1"}),
        (CrudOperation.EXISTS_SOME, "exists_some", {"obj_ids": ["id-1"]}),
    ],
)
def test_crud_dispatch(
    repo: SARepository,
    monkeypatch: pytest.MonkeyPatch,
    operation: CrudOperation,
    method_name: str,
    kwargs: dict[str, Any],
) -> None:
    sentinel = object()

    def _fake_method(*args: Any, **inner_kwargs: Any) -> object:
        assert "session" in inner_kwargs
        return sentinel

    monkeypatch.setattr(repo, method_name, _fake_method)

    with repo.uow() as uow:
        result = repo.crud(
            uow,
            "user",
            RepoModel,
            operation,
            return_id=False,
            filter=None,
            limit=0,
            offset=0,
            **kwargs,
        )
    assert result is sentinel


def test_create_read_update_upsert_delete_and_exists(repo: SARepository) -> None:
    created_one = repo.create_one(RepoModel, "user", _make_obj(1))
    assert isinstance(created_one, RepoModel)
    assert created_one.id == "id-1"

    read_one = cast(RepoModel, repo.read_one(RepoModel, "id-1"))
    assert read_one.value == 1

    created_some = repo.create_some(RepoModel, "user", [_make_obj(2), _make_obj(3)])
    assert len(created_some) == 2

    read_some = cast(
        list[RepoModel], repo.read_some(RepoModel, ["id-1", "id-2", "id-3"])
    )
    assert [x.id for x in read_some] == ["id-1", "id-2", "id-3"]

    read_all = repo.read_all(RepoModel, filter=None)
    assert len(read_all) == 3

    read_ids = repo.read_all(RepoModel, filter=None, return_id=True)
    assert set(read_ids) == {"id-1", "id-2", "id-3"}

    updated_one = repo.update_one(RepoModel, "user", _make_obj(1, value=10))
    assert isinstance(updated_one, RepoModel)
    assert updated_one.value == 10

    updated_some = cast(
        list[RepoModel],
        repo.update_some(
            RepoModel,
            "user",
            [_make_obj(2, value=20), _make_obj(3, value=30)],
        ),
    )
    assert [x.value for x in updated_some] == [20, 30]

    upserted_one_existing = repo.upsert_one(RepoModel, "user", _make_obj(1, value=11))
    assert isinstance(upserted_one_existing, RepoModel)
    assert upserted_one_existing.value == 11

    upserted_one_new = repo.upsert_one(RepoModel, "user", _make_obj(4, value=40))
    assert isinstance(upserted_one_new, RepoModel)
    assert upserted_one_new.id == "id-4"

    upserted_some = repo.upsert_some(
        RepoModel,
        "user",
        [_make_obj(3, value=33), _make_obj(5, value=50)],
    )
    assert len(upserted_some) == 2

    assert repo.exists_one(RepoModel, "id-5") is True
    assert repo.exists_some(RepoModel, ["id-1", "id-999"]) == [True, False]

    deleted_one_id = repo.delete_one(RepoModel, "user", "id-5")
    assert deleted_one_id == "id-5"

    deleted_some_ids = repo.delete_some(RepoModel, "user", ["id-4"])
    assert deleted_some_ids == ["id-4"]

    deleted_by_filter = repo.delete_all(
        RepoModel,
        "user",
        EqualsStringFilter(key="label", value="l-3"),
        return_id=True,
    )
    assert deleted_by_filter == ["id-3"]

    deleted_all_ids = repo.delete_all(RepoModel, "user", None, return_id=True)
    assert set(deleted_all_ids or []) == {"id-1", "id-2"}
    assert repo.read_all(RepoModel, None) == []


def test_read_some_raises_invalid_ids(repo: SARepository) -> None:
    with pytest.raises(exc.InvalidIdsError, match="3132db4e"):
        repo.read_some(RepoModel, ["missing-id"])


def test_create_some_and_upsert_some_validation(repo: SARepository) -> None:
    with pytest.raises(ValueError, match="Not all objs are of type RepoModel"):
        repo.create_some(RepoModel, "user", cast(Iterable[Model], [object()]))

    with pytest.raises(ValueError, match="Not all objs are of type RepoModel"):
        repo.upsert_some(RepoModel, "user", cast(Iterable[Model], [object()]))

    assert repo.upsert_some(RepoModel, "user", []) == []


def test_read_fields(repo: SARepository) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2)])

    with repo.uow() as uow:
        values = list(
            repo.read_fields(
                uow,
                "user",
                RepoModel,
                ["id", "value"],
                EqualsNumberFilter(key="value", value=2),
            )
        )
    assert values == [("id-2", 2)]


def test_split_filter_and_get_where_clause(repo: SARepository) -> None:
    mapper = repo.get_mapper(RepoModel)
    row_class = mapper.row_class

    only_db_filter = EqualsNumberFilter(key="value", value=1)
    where_filter, remainder_filter = repo.split_filter(RepoModel, only_db_filter)
    assert where_filter is not None
    assert remainder_filter is None

    mixed_filter = CompositeFilter(
        operator=LogicalOperator.AND,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsStringFilter(key="unknown", value="x"),
        ],
    )
    where_filter2, remainder_filter2 = repo.split_filter(RepoModel, mixed_filter)
    assert where_filter2 is not None
    assert remainder_filter2 is not None

    where_clause = repo.get_where_clause_from_filter(row_class, mapper, only_db_filter)
    assert where_clause is not None


def test_print_db_content(
    repo: SARepository, capsys: pytest.CaptureFixture[str]
) -> None:
    repo.create_one(RepoModel, "user", _make_obj(1))
    repo.print_db_content(RepoModel, header="H: ")
    out = capsys.readouterr().out
    assert "H:" in out
    assert "SARepoModel" in out


def test_verify_valid_ids(repo: SARepository) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2)])

    with repo.uow() as uow:
        repo.verify_valid_ids(uow, "user", RepoModel, ["id-1", "id-2"])

        with pytest.raises(exc.DuplicateIdsError, match="aac3e2af"):
            repo.verify_valid_ids(uow, "user", RepoModel, ["id-1", "id-1"])

        with pytest.raises(exc.InvalidIdsError, match="e1eb6e15"):
            repo.verify_valid_ids(uow, "user", RepoModel, ["id-1", "missing"])


def test_create_repository_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def _fake_create_sa_repository(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "repo"  # type: ignore[return-value]

    monkeypatch.setattr(
        SARepository, "create_sa_repository", _fake_create_sa_repository
    )
    result = SARepository.create_repository(
        entities=[RepoModel.ENTITY],
        connection_string="sqlite:///:memory:",
    )

    assert cast(Any, result) == "repo"
    assert captured["entities"] == [RepoModel.ENTITY]
    assert captured["connection_string"] == "sqlite:///:memory:"


def test_clear_repository_content_smoke_in_memory() -> None:
    SARepository.clear_repository_content(
        entities=[RepoModel.ENTITY],
        connection_string="sqlite:///:memory:",
    )


def test_create_sa_repository(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "repo.sqlite"
    repo = SARepository.create_sa_repository(
        entities=[],
        connection_string=f"sqlite:///{sqlite_file.as_posix()}",
        recreate_sqlite_file=True,
        register_mappers=False,
    )
    assert isinstance(repo, SARepository)


def test_create_sa_repository_sqlite_shared_memory_uri() -> None:
    """Shared-memory sqlite URI strings should be accepted by SARepository."""
    repo = SARepository.create_sa_repository(
        entities=[],
        connection_string="sqlite:///file:test_mem?mode=memory&cache=shared",
        register_mappers=False,
    )
    assert isinstance(repo, SARepository)


def test_create_sa_repository_does_not_create_non_sqlite_schema_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SQL Server schema changes must go through Alembic, not API startup."""
    engine = sa.create_engine("sqlite:///:memory:")
    monkeypatch.setattr(
        "gen_epix.fastapp.repositories.sa.repository.EngineFactory.create_engine",
        lambda *args, **kwargs: engine,
    )

    repo = SARepository.create_sa_repository(
        entities=[RepoModel.ENTITY],
        connection_string="mssql+pyodbc://example.invalid/test",
        register_mappers=False,
    )

    assert isinstance(repo, SARepository)
    assert "repo_model" not in sa.inspect(engine).get_table_names()


def test_test_connection() -> None:
    assert SARepository.test_connection("sqlite:///:memory:") is None
    assert SARepository.test_connection("not-a-valid-sqlalchemy-url") is not None
