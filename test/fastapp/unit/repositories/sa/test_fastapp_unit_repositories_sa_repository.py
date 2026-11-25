from __future__ import annotations

import uuid
from collections.abc import Iterable, Iterator
from contextlib import nullcontext
from enum import Enum
from pathlib import Path
from test.util.mock_compat import Mock
from typing import Any, ClassVar, cast

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import dialect as MSSQLDialect
from sqlalchemy.dialects.mssql.pyodbc import MSDialect_pyodbc
from sqlalchemy.orm import Session, declarative_base

import gen_epix.fastapp.exc as exc
import gen_epix.fastapp.repositories.sa.repository as repository_module
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, IsolationLevel
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import SAMapper
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.filter import (
    ComparisonOperator,
    CompositeFilter,
    ContainsStringFilter,
    EqualsNumberFilter,
    EqualsStringFilter,
    ExistsFilter,
    Filter,
    LogicalOperator,
    NoFilter,
    NumberRangeFilter,
    NumberSetFilter,
    StringSetFilter,
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


class UnsupportedFilter(Filter):
    def _match(self, value: Any) -> bool:
        return True


def _make_obj(idx: int, *, value: int | None = None) -> RepoModel:
    return RepoModel(
        id=f"id-{idx}", value=idx if value is None else value, label=f"l-{idx}"
    )


@pytest.fixture
def engine() -> sa.Engine:
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(name="repo")
def repository_fixture(engine: sa.Engine) -> Iterator[SARepository]:
    """Provide a SQLite repository with a registered test model."""
    repository = SARepository(
        engine,
        id="repo-id",
        name="repo-name",
        register_mappers=False,
    )
    repository.register_mapper(SAMapper(RepoModel, SARepoModel))
    try:
        yield repository
    finally:
        engine.dispose(close=True)


def test_repository_properties_and_session(repo: SARepository) -> None:
    assert repo.id == "repo-id"
    assert repo.name == "repo-name"
    assert repo.default_isolation_level == IsolationLevel.SERIALIZABLE

    repo.default_isolation_level = IsolationLevel.READ_COMMITTED
    assert repo.default_isolation_level == IsolationLevel.READ_COMMITTED

    session = repo.get_session(expire_on_commit=True)
    assert isinstance(session, Session)
    session.close()


@pytest.mark.parametrize("level", list(IsolationLevel))
def test_sqlite_session_isolation_level(
    repo: SARepository, level: IsolationLevel
) -> None:
    """Check the effective isolation level on a real SQLite connection."""
    expected = (
        "READ UNCOMMITTED"
        if level is IsolationLevel.READ_UNCOMMITTED
        else "SERIALIZABLE"
    )
    with repo.get_session(isolation_level=level) as session:
        assert session.scalar(sa.text("SELECT 1")) == 1
        assert session.connection().get_isolation_level() == expected


@pytest.mark.parametrize("level", list(IsolationLevel))
def test_mssql_session_isolation_level(level: IsolationLevel) -> None:
    """Check the SQL Server session configuration without connecting."""

    def unexpected_connect() -> Any:
        pytest.fail("Isolation level validation must not open a database connection")

    mssql_engine = sa.create_engine("mssql+pyodbc://", creator=unexpected_connect)
    repository = SARepository(mssql_engine, register_mappers=False)
    with repository.get_session(isolation_level=level) as session:
        value = session.get_bind().get_execution_options()["isolation_level"]
    assert value == level.name.replace("_", " ")
    supported_levels = MSDialect_pyodbc().get_isolation_level_values(None)  # type: ignore[arg-type]
    assert value in supported_levels


def test_invalid_isolation_mapping_fails_during_repository_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject an invalid mapping before the repository can open a session."""
    sqlite_engine = sa.create_engine("sqlite://")
    monkeypatch.setattr(
        sqlite_engine.dialect, "get_isolation_level_values", lambda _: ["SERIALIZABLE"]
    )
    with pytest.raises(sa.exc.ArgumentError, match="sqlite.*READ UNCOMMITTED"):
        SARepository(sqlite_engine, register_mappers=False)


def test_uow_nested_and_invalid_nested_kwargs(repo: SARepository) -> None:
    with repo.uow() as outer_uow:
        session = cast(SAUnitOfWork, outer_uow).session
        close = Mock(wraps=session.close)
        session.close = close
        nested_uow = repo.uow()
        assert isinstance(nested_uow, SAUnitOfWork)
        assert nested_uow.session is session
        with nested_uow:
            pass
        close.assert_not_called()
        with pytest.raises(exc.RepositoryServiceError, match="b78b8c87"):
            repo.uow(invalid=True)
    close.assert_called_once_with()


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


def test_in_session_read_some_optimized_sqlite_path(repo: SARepository) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2)])
    mapper = repo.get_mapper(RepoModel)

    with repo.get_session() as session:
        rows, row_ids = SARepository._in_session_read_some(
            mapper, session, ["id-2", "id-1"], optimize_parameter_handling=True
        )

    assert row_ids == ["id-1", "id-2"]
    assert {row.id for row in rows} == {"id-1", "id-2"}


def test_exists_some_accepts_generator_ids_in_input_order(repo: SARepository) -> None:
    repo.create_one(RepoModel, "user", _make_obj(1))

    result = repo.exists_some(RepoModel, (obj_id for obj_id in ["id-1", "missing-id"]))

    assert result == [True, False]


def test_delete_some_uses_supplied_session_for_uncommitted_rows(
    repo: SARepository,
) -> None:
    with repo.get_session() as session:
        session.add(repo.to_sql("user", RepoModel, _make_obj(1)))
        session.flush()

        assert repo.delete_some(RepoModel, "user", ["id-1"], session=session) == [
            "id-1"
        ]
        assert repo.exists_some(RepoModel, ["id-1"], session=session) == [False]


def test_delete_some_rejects_missing_ids(repo: SARepository) -> None:
    with pytest.raises(exc.InvalidIdsError, match="8e431d94") as error:
        repo.delete_some(RepoModel, "user", ["missing-id"])

    assert error.value.ids == ["missing-id"]


def test_read_some_reports_duplicate_ids(repo: SARepository) -> None:
    repo.create_one(RepoModel, "user", _make_obj(1))

    with pytest.raises(exc.DuplicateIdsError, match="bba17339") as error:
        repo.read_some(RepoModel, ["id-1", "id-1"])

    assert error.value.ids == ["id-1"]


def test_create_some_and_upsert_some_validation(repo: SARepository) -> None:
    with pytest.raises(ValueError, match="Not all objs are of type RepoModel"):
        repo.create_some(RepoModel, "user", cast(Iterable[Model], [object()]))

    with pytest.raises(ValueError, match="Not all objs are of type RepoModel"):
        repo.upsert_some(RepoModel, "user", cast(Iterable[Model], [object()]))

    assert repo.upsert_some(RepoModel, "user", []) == []


def test_mutating_batches_reject_duplicate_ids(repo: SARepository) -> None:
    duplicate_objs = [_make_obj(1), _make_obj(1)]

    with pytest.raises(exc.DuplicateIdsError):
        repo.create_some(RepoModel, "user", duplicate_objs)

    repo.create_one(RepoModel, "user", _make_obj(1))
    with pytest.raises(exc.DuplicateIdsError):
        repo.update_some(RepoModel, "user", duplicate_objs)
    with pytest.raises(exc.DuplicateIdsError):
        repo.upsert_some(RepoModel, "user", duplicate_objs)
    with pytest.raises(exc.DuplicateIdsError):
        repo.delete_some(RepoModel, "user", ["id-1", "id-1"])


def test_create_some_exact_batch_without_flush(repo: SARepository) -> None:
    repo._max_insert_batch_size = 2  # pylint: disable=protected-access

    created = [
        cast(RepoModel, obj)
        for obj in repo.create_some(
            RepoModel, "user", [_make_obj(1), _make_obj(2)], flush=False
        )
    ]

    assert [obj.id for obj in created] == ["id-1", "id-2"]
    assert repo.exists_some(RepoModel, ["id-1", "id-2"]) == [True, True]


def test_create_some_without_flush_rejects_multiple_batches(
    repo: SARepository,
) -> None:
    repo._max_insert_batch_size = 1  # pylint: disable=protected-access
    objs = [_make_obj(1), _make_obj(2)]

    with pytest.raises(exc.RepositoryServiceError, match="fa00ce85"):
        repo.create_some(RepoModel, "user", objs, flush=False)


@pytest.mark.parametrize(
    ("filter_", "limit", "offset", "expected_ids"),
    [
        pytest.param(
            EqualsNumberFilter(key="value", value=1),
            2,
            2,
            [],
            id="offset-past-end",
        ),
        pytest.param(
            EqualsNumberFilter(key="value", value=99),
            2,
            0,
            [],
            id="empty-filter-result",
        ),
        pytest.param(
            NumberRangeFilter(
                key="value",
                lower_bound=1,
                upper_bound=3,
                upper_bound_censor=ComparisonOperator.STE,
            ),
            0,
            0,
            ["id-1", "id-2", "id-3"],
            id="unbounded",
        ),
        pytest.param(
            NumberRangeFilter(
                key="value",
                lower_bound=1,
                upper_bound=3,
                upper_bound_censor=ComparisonOperator.STE,
            ),
            2,
            2,
            ["id-3"],
            id="page-reaches-end",
        ),
        pytest.param(
            NumberRangeFilter(key="value", lower_bound=1, upper_bound=3),
            1,
            1,
            ["id-2"],
            id="bounded-page",
        ),
    ],
)
def test_apply_read_all_obj_pagination_boundaries(
    repo: SARepository,
    filter_: Any,
    limit: int,
    offset: int,
    expected_ids: list[str],
) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2), _make_obj(3)])
    result = cast(
        list[RepoModel],
        repo.read_all(RepoModel, None, obj_filter=filter_, limit=limit, offset=offset),
    )

    assert [obj.id for obj in result] == expected_ids


def test_read_all_applies_zero_range_bound(repo: SARepository) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(-1), _make_obj(0), _make_obj(1)])

    objs = [
        cast(RepoModel, obj)
        for obj in repo.read_all(
            RepoModel,
            NumberRangeFilter(key="value", lower_bound=0, upper_bound=1),
        )
    ]

    assert [obj.id for obj in objs] == ["id-0"]


def test_crud_return_ids_pagination_and_object_filter(repo: SARepository) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2), _make_obj(3)])

    updated_ids = repo.update_some(
        RepoModel, "user", [_make_obj(1, value=10)], return_id=True
    )
    assert updated_ids == ["id-1"]

    upserted_ids = repo.upsert_some(
        RepoModel,
        "user",
        [_make_obj(2, value=20), _make_obj(4, value=40)],
        return_id=True,
    )
    assert upserted_ids == ["id-2", "id-4"]

    page = repo.read_all(RepoModel, filter=None, limit=2, offset=1)
    assert len(page) == 2

    filtered_ids = repo.read_all(
        RepoModel,
        filter=None,
        return_id=True,
        obj_filter=EqualsNumberFilter(key="value", value=20),
    )
    assert filtered_ids == ["id-2"]


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


@pytest.mark.parametrize(
    ("filter_", "expected_ids"),
    [
        pytest.param(ExistsFilter(key="label"), ["id-1", "id-2", "id-3"], id="exists"),
        pytest.param(ExistsFilter(key="label", invert=True), [], id="not-exists"),
        pytest.param(
            StringSetFilter(key="label", members=frozenset({"l-1", "l-3"})),
            ["id-1", "id-3"],
            id="string-set",
        ),
        pytest.param(
            NumberSetFilter(key="value", members=frozenset({1, 3}), invert=True),
            ["id-2"],
            id="inverted-number-set",
        ),
        pytest.param(
            NumberRangeFilter(
                key="value",
                lower_bound=1,
                lower_bound_censor=ComparisonOperator.GT,
                upper_bound=3,
                upper_bound_censor=ComparisonOperator.STE,
            ),
            ["id-2", "id-3"],
            id="bounded-range",
        ),
        pytest.param(
            NumberRangeFilter(
                key="value",
                lower_bound=2,
                lower_bound_censor=ComparisonOperator.GT,
            ),
            ["id-3"],
            id="lower-only-range",
        ),
        pytest.param(
            NumberRangeFilter(
                key="value",
                upper_bound=1,
                upper_bound_censor=ComparisonOperator.STE,
            ),
            ["id-1"],
            id="upper-only-range",
        ),
    ],
)
def test_read_all_translates_exists_set_and_range_filters(
    repo: SARepository, filter_: Any, expected_ids: list[str]
) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2), _make_obj(3)])

    objs = cast(list[RepoModel], repo.read_all(RepoModel, filter_))

    assert [obj.id for obj in objs] == expected_ids


def test_split_filter_keeps_or_with_unmapped_branch_in_python(
    repo: SARepository,
) -> None:
    filter_ = CompositeFilter(
        operator=LogicalOperator.OR,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsStringFilter(key="unknown", value="x"),
        ],
    )

    where_filter, remainder_filter = repo.split_filter(RepoModel, filter_)

    assert where_filter is None
    assert remainder_filter == filter_


def test_split_filter_handles_empty_and_and_composites(repo: SARepository) -> None:
    only_sql_filter = EqualsNumberFilter(key="value", value=1)
    only_python_filter = EqualsStringFilter(key="unknown", value="x")

    assert repo.split_filter(RepoModel, None) == (None, None)
    assert repo.split_filter(
        RepoModel,
        CompositeFilter(operator=LogicalOperator.AND, filters=[only_sql_filter]),
    ) == (only_sql_filter, None)
    assert repo.split_filter(
        RepoModel,
        CompositeFilter(operator=LogicalOperator.AND, filters=[only_python_filter]),
    ) == (None, only_python_filter)


@pytest.mark.parametrize("operator", [LogicalOperator.AND, LogicalOperator.OR])
def test_split_filter_preserves_inversion_for_sql_composites(
    repo: SARepository, operator: LogicalOperator
) -> None:
    filter_ = CompositeFilter(
        operator=operator,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsNumberFilter(key="value", value=2),
        ],
        invert=True,
    )

    where_filter, remainder_filter = repo.split_filter(RepoModel, filter_)

    assert where_filter == CompositeFilter(
        operator=operator,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsNumberFilter(key="value", value=2),
        ],
        invert=True,
    )
    assert remainder_filter is None


def test_split_filter_keeps_inverted_mixed_and_in_python(
    repo: SARepository,
) -> None:
    filter_ = CompositeFilter(
        operator=LogicalOperator.AND,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsStringFilter(key="unknown", value="x"),
        ],
        invert=True,
    )

    assert repo.split_filter(RepoModel, filter_) == (None, filter_)


def test_split_filter_drops_no_filter(repo: SARepository) -> None:
    only_sql_filter = EqualsNumberFilter(key="value", value=1)

    assert repo.split_filter(RepoModel, NoFilter()) == (None, None)
    assert repo.split_filter(
        RepoModel,
        CompositeFilter(
            operator=LogicalOperator.AND, filters=[NoFilter(), only_sql_filter]
        ),
    ) == (only_sql_filter, None)


def test_split_filter_keeps_inverted_no_filter_in_python(repo: SARepository) -> None:
    inverted_no_filter = NoFilter(invert=True)

    assert repo.split_filter(RepoModel, inverted_no_filter) == (
        None,
        inverted_no_filter,
    )


@pytest.mark.parametrize(
    ("obj_filter", "limit", "offset", "expected_ids"),
    [
        pytest.param(
            NumberSetFilter(key="value", members=frozenset({1, 3})),
            0,
            0,
            ["id-1", "id-3"],
            id="filter",
        ),
        pytest.param(
            NumberSetFilter(key="value", members=frozenset({1, 2, 3})),
            1,
            1,
            ["id-2"],
            id="filter-and-page",
        ),
        pytest.param(NoFilter(invert=True), 0, 0, [], id="inverted-no-filter"),
    ],
)
def test_read_all_ids_with_obj_filter_selects_rows_once(
    repo: SARepository,
    engine: sa.Engine,
    obj_filter: Any,
    limit: int,
    offset: int,
    expected_ids: list[str],
) -> None:
    # One parameter per id in a second query fails on SQL Server beyond 2100 ids
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2), _make_obj(3)])
    statements: list[str] = []

    def _record(*args: Any) -> None:
        statements.append(args[2])

    sa.event.listen(engine, "before_cursor_execute", _record)
    try:
        ids = repo.read_all(
            RepoModel,
            None,
            return_id=True,
            obj_filter=obj_filter,
            limit=limit,
            offset=offset,
        )
    finally:
        sa.event.remove(engine, "before_cursor_execute", _record)

    assert ids == expected_ids
    selects = [x for x in statements if x.lstrip().upper().startswith("SELECT")]
    assert len(selects) == 1
    assert " IN " not in selects[0].upper()


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

        with pytest.raises(exc.DuplicateIdsError, match="aac3e2af") as error:
            repo.verify_valid_ids(uow, "user", RepoModel, ["id-1", "id-1"])
        assert error.value.ids == ["id-1"]

        with pytest.raises(exc.InvalidIdsError, match="e1eb6e15"):
            repo.verify_valid_ids(uow, "user", RepoModel, ["id-1", "missing"])


@pytest.mark.parametrize(
    "obj_ids, row_ids, code, message",
    [
        (["missing"], [], "3132db4e", "custom_table"),
        (["id-1", "missing"], ["id-1"], "35de72de", "custom_table"),
    ],
)
def test_in_session_verify_retrieved_ids_reports_missing_ids(
    repo: SARepository,
    obj_ids: list[str],
    row_ids: list[str],
    code: str,
    message: str,
) -> None:
    with pytest.raises(exc.InvalidIdsError, match=code) as error:
        SARepository._in_session_verify_retrieved_ids(
            repo.get_mapper(RepoModel), obj_ids, row_ids, table_name=message
        )

    assert message in str(error.value)


def test_verify_duplicate_ids_accepts_unique_iterable() -> None:
    SARepository._verify_duplicate_ids(RepoModel, (obj_id for obj_id in ["a", "b"]))


def test_verify_duplicate_ids_reports_all_repeated_values() -> None:
    with pytest.raises(exc.DuplicateIdsError, match="bba17339") as error:
        SARepository._verify_duplicate_ids(RepoModel, ["a", "b", "a", "b"])

    assert error.value.ids == ["a", "b"]


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


def test_clear_repository_content_disposes_engine_for_default_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    dispose = Mock(wraps=engine.dispose)
    monkeypatch.setattr(engine, "dispose", dispose)
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )

    SARepository.clear_repository_content(
        entities=[RepoModel.ENTITY], connection_string="sqlite:///:memory:"
    )

    dispose.assert_called_once_with()


def test_clear_repository_content_disposes_engine_when_inspection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )
    monkeypatch.setattr(
        repository_module, "inspect", Mock(side_effect=RuntimeError("inspect failed"))
    )

    with pytest.raises(RuntimeError, match="inspect failed"):
        SARepository.clear_repository_content(
            entities=[], connection_string="sqlite:///:memory:"
        )

    engine.dispose.assert_called_once_with()


def test_clear_repository_content_drops_default_schema_tables(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "clear.sqlite"
    connection_string = f"sqlite:///{sqlite_file.as_posix()}"
    repo = SARepository.create_sa_repository(
        entities=[RepoModel.ENTITY],
        connection_string=connection_string,
        recreate_sqlite_file=True,
    )
    repo._engine.dispose()  # pylint: disable=protected-access

    SARepository.clear_repository_content(
        entities=[RepoModel.ENTITY], connection_string=connection_string
    )

    engine = sa.create_engine(connection_string)
    try:
        assert "repo_model" not in sa.inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_create_sa_repository_with_sqlite_scheme() -> None:
    repo = SARepository.create_sa_repository(
        entities=[RepoModel.ENTITY],
        connection_string="sqlite://",
        register_mappers=False,
    )
    try:
        assert "repo_model" in sa.inspect(repo._engine).get_table_names()
    finally:
        repo._engine.dispose()


def test_create_sa_repository_disposes_engine_when_entity_metadata_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    monkeypatch.setattr(
        SARepository,
        "_create_sqlite_engine",
        lambda *args, **kwargs: engine,
    )
    entity = Entity(persistable=True, table_name="missing_model", id_field_name="id")
    entity.set_model_class(RepoModel)

    with pytest.raises(ValueError, match="does not have a db_model_class"):
        SARepository.create_sa_repository(
            entities=[entity],
            connection_string="sqlite:///:memory:",
            register_mappers=False,
        )

    engine.dispose.assert_called_once_with()


def test_create_sa_repository(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "repo.sqlite"
    repo = SARepository.create_sa_repository(
        entities=[],
        connection_string=f"sqlite:///{sqlite_file.as_posix()}",
        recreate_sqlite_file=True,
        register_mappers=False,
    )
    try:
        assert isinstance(repo, SARepository)
    finally:
        repo._engine.dispose(close=True)


def test_create_sa_repository_sqlite_shared_memory_uri() -> None:
    """Shared-memory sqlite URI strings should be accepted by SARepository."""
    repo = SARepository.create_sa_repository(
        entities=[],
        connection_string="sqlite:///file:test_mem?mode=memory&cache=shared",
        register_mappers=False,
    )
    try:
        assert isinstance(repo, SARepository)
    finally:
        repo._engine.dispose(close=True)


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


def test_create_sa_repository_default_sqlite_is_in_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    repo = SARepository.create_sa_repository(entities=[], register_mappers=False)

    assert isinstance(repo, SARepository)
    assert list(tmp_path.iterdir()) == []


def test_create_sa_repository_attached_sqlite_is_in_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    entity = Entity(
        persistable=True,
        schema_name="test_schema",
        table_name="repo_model",
        id_field_name="id",
    )
    entity.set_model_class(RepoModel).set_db_model_class(SARepoModel)
    second_entity = entity.model_copy(update={"schema_name": "second_schema"})

    repo = SARepository.create_sa_repository(
        entities=[entity, second_entity], register_mappers=False
    )

    assert isinstance(repo, SARepository)
    assert list(tmp_path.iterdir()) == []


def test_test_connection() -> None:
    assert SARepository.test_connection("sqlite:///:memory:") is None
    assert SARepository.test_connection("not-a-valid-sqlalchemy-url") is not None


def test_test_connection_disposes_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    """The probe engine is disposed whether or not the connection succeeds."""
    engine = Mock()
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(sa, "create_engine", create_engine)

    assert SARepository.test_connection("mssql+pyodbc://db", timeout=30) is None
    create_engine.assert_called_once_with(
        "mssql+pyodbc://db", connect_args={"timeout": 30}
    )
    engine.connect.return_value.close.assert_called_once_with()
    engine.dispose.assert_called_once_with()

    error = RuntimeError("Login timeout expired")
    engine.connect.side_effect = error
    assert SARepository.test_connection("mssql+pyodbc://db") is error
    assert engine.dispose.call_count == 2


def test_clear_repository_content_drops_alembic_tracking_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """clear_repository_content(alembic_schema=...) also drops the Alembic

    version-tracking table (and its schema), so a subsequent `alembic upgrade
    head` starts from a clean slate instead of thinking migrations already ran."""
    main_file = tmp_path / "clear_alembic.sqlite"
    alembic_file = tmp_path / "clear_alembic_tracking.sqlite"
    connection_string = f"sqlite:///{main_file.as_posix()}"
    engine = sa.create_engine(connection_string)

    @sa.event.listens_for(engine, "connect")
    def _attach_alembic_schema(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"ATTACH DATABASE '{alembic_file.as_posix()}' AS alembic")
        cursor.close()

    monkeypatch.setattr(
        "gen_epix.fastapp.repositories.sa.repository.EngineFactory.create_engine",
        lambda *args, **kwargs: engine,
    )

    with engine.begin() as conn:
        conn.execute(
            sa.text(
                "CREATE TABLE alembic.alembic_version "
                "(version_num VARCHAR(32) NOT NULL)"
            )
        )
        conn.execute(sa.text("INSERT INTO alembic.alembic_version VALUES ('deadbeef')"))

    SARepository.clear_repository_content(
        entities=[], connection_string=connection_string, alembic_schema="alembic"
    )

    with engine.connect() as conn:
        tables = sa.inspect(conn).get_table_names(schema="alembic")
    assert "alembic_version" not in tables


def test_clear_repository_content_alembic_schema_defaults_to_noop() -> None:
    """Existing callers that don't pass alembic_schema are unaffected."""
    SARepository.clear_repository_content(
        entities=[RepoModel.ENTITY], connection_string="sqlite:///:memory:"
    )


def _create_alembic_tracked_repo_engine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[str, sa.Engine]:
    """A sqlite database with the repo_model table and an Alembic version stamp.

    The ``alembic`` schema is an attached database, and every engine the
    repository creates is this one, so the attachment is always there.
    """
    connection_string = f"sqlite:///{(tmp_path / 'main.sqlite').as_posix()}"
    alembic_file = tmp_path / "alembic.sqlite"
    engine = sa.create_engine(connection_string)

    @sa.event.listens_for(engine, "connect")
    def _attach_alembic_schema(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"ATTACH DATABASE '{alembic_file.as_posix()}' AS alembic")
        cursor.close()

    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )
    SARepoModel.__table__.create(engine)
    with engine.begin() as conn:
        conn.execute(
            sa.text(
                "CREATE TABLE alembic.alembic_version "
                "(version_num VARCHAR(32) NOT NULL)"
            )
        )
        conn.execute(sa.text("INSERT INTO alembic.alembic_version VALUES ('deadbeef')"))
    return connection_string, engine


def test_find_remaining_content_empty_after_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    connection_string, _ = _create_alembic_tracked_repo_engine(tmp_path, monkeypatch)
    kwargs = {
        "entities": [RepoModel.ENTITY],
        "connection_string": connection_string,
        "alembic_schema": "alembic",
    }

    SARepository.clear_repository_content(**kwargs)

    assert not SARepository.find_remaining_content(**kwargs)


def test_find_remaining_content_reports_tables_left_by_denied_drops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """clear_repository_content swallows a denied DROP; this is what catches it."""
    connection_string, _ = _create_alembic_tracked_repo_engine(tmp_path, monkeypatch)
    monkeypatch.setattr(
        sa.Table, "drop", Mock(side_effect=RuntimeError("DROP TABLE permission denied"))
    )
    kwargs = {
        "entities": [RepoModel.ENTITY],
        "connection_string": connection_string,
        "alembic_schema": "alembic",
    }

    SARepository.clear_repository_content(**kwargs)

    assert SARepository.find_remaining_content(**kwargs) == [
        "table repo_model still exists",
        "table alembic.alembic_version still exists",
    ]


def test_find_remaining_content_reports_legacy_table_left_by_denied_drop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A table that is no longer an entity is checked too."""
    connection_string, engine = _create_alembic_tracked_repo_engine(
        tmp_path, monkeypatch
    )
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE legacy_model (id INTEGER PRIMARY KEY)"))
    drop = sa.Table.drop

    def _deny_legacy_drop(table: sa.Table, *args: Any, **kwargs: Any) -> None:
        if table.name == "legacy_model":
            raise RuntimeError("DROP TABLE permission denied")
        drop(table, *args, **kwargs)

    monkeypatch.setattr(sa.Table, "drop", _deny_legacy_drop)
    kwargs = {
        "entities": [RepoModel.ENTITY],
        "connection_string": connection_string,
        "alembic_schema": "alembic",
    }

    SARepository.clear_repository_content(**kwargs)

    assert SARepository.find_remaining_content(**kwargs) == [
        "table legacy_model still exists"
    ]


def test_find_remaining_content_disposes_engine_when_inspection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )
    inspector = Mock()
    inspector.get_table_names.side_effect = RuntimeError("permission denied")
    monkeypatch.setattr(repository_module, "inspect", Mock(return_value=inspector))

    with pytest.raises(RuntimeError, match="permission denied"):
        SARepository.find_remaining_content(
            entities=[], connection_string="mssql+pyodbc://db", alembic_schema="alembic"
        )

    engine.dispose.assert_called_once_with()


def test_find_remaining_content_requires_connection_string() -> None:
    with pytest.raises(ValueError, match="connection_string is required"):
        SARepository.find_remaining_content(entities=[])


def test_check_schema_matches_reports_missing_table(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "check_missing_table.sqlite"
    connection_string = f"sqlite:///{sqlite_file.as_posix()}"

    problems = SARepository.check_schema_matches(
        entities=[RepoModel.ENTITY], connection_string=connection_string
    )

    assert problems == ["table repo_model does not exist"]


def test_check_schema_matches_requires_connection_string() -> None:
    with pytest.raises(ValueError, match="connection_string is required"):
        SARepository.check_schema_matches(entities=[])


def test_check_schema_matches_disposes_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    dispose = Mock(wraps=engine.dispose)
    monkeypatch.setattr(engine, "dispose", dispose)
    monkeypatch.setattr(
        repository_module.EngineFactory,
        "create_engine",
        lambda *args, **kwargs: engine,
    )

    assert (
        SARepository.check_schema_matches(
            entities=[], connection_string="sqlite:///:memory:"
        )
        == []
    )

    dispose.assert_called_once_with()


def test_check_schema_matches_disposes_engine_when_inspection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    monkeypatch.setattr(
        repository_module.EngineFactory,
        "create_engine",
        lambda *args, **kwargs: engine,
    )
    monkeypatch.setattr(
        repository_module, "inspect", Mock(side_effect=RuntimeError("inspect failed"))
    )

    with pytest.raises(RuntimeError, match="inspect failed"):
        SARepository.check_schema_matches(
            entities=[], connection_string="sqlite:///:memory:"
        )

    engine.dispose.assert_called_once_with()


def test_create_sa_repository_rejects_nonexistent_sqlite_file(tmp_path: Path) -> None:
    connection_string = f"sqlite:///{(tmp_path / 'missing.sqlite').as_posix()}"

    with pytest.raises(ValueError, match="Unable to derive file"):
        SARepository.create_sa_repository(
            entities=[], connection_string=connection_string
        )


def test_check_schema_matches_empty_for_matching_schema(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "check_match.sqlite"
    connection_string = f"sqlite:///{sqlite_file.as_posix()}"
    repo = SARepository.create_sa_repository(
        entities=[RepoModel.ENTITY],
        connection_string=connection_string,
        recreate_sqlite_file=True,
    )
    repo._engine.dispose()  # pylint: disable=protected-access

    problems = SARepository.check_schema_matches(
        entities=[RepoModel.ENTITY], connection_string=connection_string
    )

    assert not problems


def test_check_schema_matches_reports_missing_column(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "check_missing_column.sqlite"
    connection_string = f"sqlite:///{sqlite_file.as_posix()}"
    engine = sa.create_engine(connection_string)
    try:
        legacy_metadata = sa.MetaData()
        sa.Table(
            "repo_model",
            legacy_metadata,
            sa.Column("id", sa.String, primary_key=True, nullable=False),
        )
        legacy_metadata.create_all(engine)
    finally:
        engine.dispose()

    problems = SARepository.check_schema_matches(
        entities=[RepoModel.ENTITY], connection_string=connection_string
    )

    assert problems == ["table repo_model is missing column(s): label, value"]


def test_create_unique_values_temp_table_batches_values() -> None:
    session = Mock()
    bind = Mock()
    bind.dialect = MSSQLDialect()
    session.get_bind.return_value = bind
    metadata = sa.MetaData()
    values = [uuid.UUID(int=1), uuid.UUID(int=2)]

    table = SARepository.create_unique_values_temp_table(
        session,
        metadata,
        "value",
        sa.Uuid(),
        values,
        max_insert_batch_size=1,
        table_name="values",
    )

    assert table.name == "#values"
    assert session.execute.call_count == 3
    assert session.flush.call_count == 2
    with pytest.raises(ValueError, match="must not contain a '#' prefix"):
        SARepository.create_unique_values_temp_table(
            session, metadata, "value", sa.Uuid(), values, table_name="#values"
        )


def test_select_with_id_join_uses_sql_server_temp_table() -> None:
    model_base = declarative_base()

    class TempJoinRow(model_base):
        __tablename__ = "temp_join_row"
        id = sa.Column(sa.String, primary_key=True)

    mapper = Mock()
    mapper.row_class = TempJoinRow
    mapper.get_row_id_column.return_value = TempJoinRow.id
    session = Mock()
    bind = Mock()
    bind.dialect = MSSQLDialect()
    session.get_bind.return_value = bind

    statement = SARepository._select_with_id_join(
        mapper, session, ["id-1", "id-2"], max_ids_in_clause=1
    )

    assert "JOIN [#temp_" in str(statement.compile(dialect=bind.dialect))
    assert session.execute.call_count == 3
    assert session.flush.call_count == 2


def test_create_repository_accepts_sqlite_file(tmp_path: Path) -> None:
    database_file = tmp_path / "repository.sqlite"
    database_file.touch()

    repository = SARepository.create_repository(
        entities=[RepoModel.ENTITY], file=database_file
    )

    try:
        assert isinstance(repository, SARepository)
        assert "repo_model" in sa.inspect(repository._engine).get_table_names()
    finally:
        repository._engine.dispose()


def test_clear_repository_content_requires_connection_string() -> None:
    with pytest.raises(ValueError, match="connection_string is required"):
        SARepository.clear_repository_content(entities=[RepoModel.ENTITY])


def test_clear_repository_content_handles_named_foreign_keys(tmp_path: Path) -> None:
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'foreign_keys.sqlite'}")
    metadata = sa.MetaData()
    sa.Table("parent", metadata, sa.Column("id", sa.Integer, primary_key=True))
    sa.Table(
        "child",
        metadata,
        sa.Column("parent_id", sa.Integer),
        sa.ForeignKeyConstraint(["parent_id"], ["parent.id"], name="fk_child_parent"),
    )
    metadata.create_all(engine)

    try:
        SARepository._clear_repository_content(engine, [RepoModel.ENTITY], None)
        assert sa.inspect(engine).get_table_names() == []
    finally:
        engine.dispose()


def test_repository_initializes_mappers_with_factory(repo: SARepository) -> None:
    mapper_factory = Mock()
    mapper = SAMapper(RepoModel, SARepoModel)
    mapper_factory.create_mapper.return_value = mapper

    repository = SARepository(
        repo._engine,
        entities=[RepoModel.ENTITY],
        sa_mapper_factory=mapper_factory,
    )

    assert repository.get_mapper(RepoModel) is mapper
    mapper_factory.create_mapper.assert_called_once_with(
        RepoModel, SARepoModel, field_name_map=None
    )


@pytest.mark.parametrize(
    ("dialect_name", "ddl_fragment"),
    [
        ("mssql", "DROP CONSTRAINT"),
        ("postgresql", "DROP CONSTRAINT"),
        ("mysql", "DROP FOREIGN KEY"),
        ("sqlite", "DROP CONSTRAINT"),
    ],
)
def test_clear_repository_content_uses_dialect_specific_constraint_ddl(
    monkeypatch: pytest.MonkeyPatch, dialect_name: str, ddl_fragment: str
) -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = ["child"]
    inspector.get_foreign_keys.return_value = [{"name": "fk_child_parent"}]
    monkeypatch.setattr(repository_module, "inspect", lambda engine: inspector)
    engine = Mock()
    connection = Mock()
    connection.dialect.name = dialect_name
    connection.dialect.identifier_preparer.quote.side_effect = (
        lambda value: f"`{value}`"
    )
    engine.connect.side_effect = lambda: nullcontext(connection)

    SARepository._clear_repository_content(engine, [RepoModel.ENTITY], None)

    statements = [str(call.args[0]) for call in connection.execute.call_args_list]
    assert any(ddl_fragment in statement for statement in statements)
    connection.begin.return_value.commit.assert_called_once_with()


def test_clear_repository_content_continues_when_schema_inspection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspector = Mock()
    inspector.get_table_names.side_effect = RuntimeError("schema unavailable")
    monkeypatch.setattr(repository_module, "inspect", lambda engine: inspector)
    engine = Mock()
    connection = Mock()
    engine.connect.side_effect = lambda: nullcontext(connection)

    SARepository._clear_repository_content(engine, [RepoModel.ENTITY], None)

    connection.commit.assert_called_once_with()


def test_in_session_read_some_optimized_path_accepts_empty_ids(
    repo: SARepository,
) -> None:
    with repo.get_session() as session:
        rows, row_ids = SARepository._in_session_read_some(
            repo.get_mapper(RepoModel),
            session,
            [],
            optimize_parameter_handling=True,
        )

    assert rows == []
    assert row_ids == []


def test_filter_where_clause_supports_column_functions_and_full_ranges(
    repo: SARepository,
) -> None:
    row_class = repo.get_mapper(RepoModel).row_class
    contains_clause = repo.get_where_clause_from_filter(
        row_class,
        None,
        ContainsStringFilter(key="label", value="L", invert=True),
        column_function_map={"label": sa.func.lower},
    )
    range_clause = repo.get_where_clause_from_filter(
        row_class,
        None,
        NumberRangeFilter(
            key="value",
            lower_bound=1,
            lower_bound_censor=ComparisonOperator.GT,
            upper_bound=3,
            upper_bound_censor=ComparisonOperator.ST,
            invert=True,
        ),
    )

    assert "lower(repo_model.label)" in str(contains_clause)
    assert "NOT" in str(contains_clause).upper()
    assert "NOT" in str(range_clause).upper()


def test_create_sqlite_engine_attaches_memory_schema() -> None:
    engine = SARepository._create_sqlite_engine(
        None, {"attached"}, echo=False, recreate_sqlite_file=False
    )

    try:
        with engine.connect() as connection:
            assert "attached" in sa.inspect(connection).get_schema_names()
    finally:
        engine.dispose()


def test_create_sqlite_repository_recreates_existing_file(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "recreated.sqlite"
    connection_string = f"sqlite:///{sqlite_file.as_posix()}"
    old_engine = sa.create_engine(connection_string)
    with old_engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE stale (id INTEGER PRIMARY KEY)"))
    old_engine.dispose()

    repository = SARepository.create_sa_repository(
        entities=[],
        connection_string=connection_string,
        recreate_sqlite_file=True,
        register_mappers=False,
    )

    try:
        assert sa.inspect(repository._engine).get_table_names() == []
    finally:
        repository._engine.dispose()


def test_create_non_sqlite_engine_creates_requested_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    connection = Mock()
    connection.dialect.has_schema.return_value = False
    engine.connect.side_effect = lambda: nullcontext(connection)
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(repository_module.EngineFactory, "create_engine", create_engine)

    result = SARepository._create_non_sqlite_engine(
        "postgresql://db",
        {"app_schema"},
        echo=True,
        create_database_objects=True,
        connect_args={"timeout": 5},
    )

    assert result is engine
    create_engine.assert_called_once_with(
        "postgresql://db", True, connect_args={"timeout": 5}
    )
    assert isinstance(connection.execute.call_args.args[0], sa.schema.CreateSchema)
    connection.commit.assert_called_once_with()


def test_get_repository_metadata_rejects_missing_db_model() -> None:
    entity = Entity(persistable=True, table_name="missing_model", id_field_name="id")
    entity.set_model_class(RepoModel)

    with pytest.raises(ValueError, match="does not have a db_model_class"):
        SARepository._get_repository_metadata([entity])


def test_check_schema_matches_reports_schema_inspection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    inspector = Mock()
    inspector.get_table_names.side_effect = RuntimeError("schema unavailable")
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )

    problems = SARepository.check_schema_matches(
        entities=[RepoModel.ENTITY], connection_string="sqlite:///:memory:"
    )

    assert problems == ["schema None could not be inspected: schema unavailable"]
    engine.dispose.assert_called_once_with()


def test_clear_repository_content_skips_uninspectable_foreign_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = ["child"]
    inspector.get_foreign_keys.side_effect = RuntimeError("cannot inspect table")
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    engine = sa.create_engine("sqlite:///:memory:")

    try:
        SARepository._clear_repository_content(engine, [RepoModel.ENTITY], None)
    finally:
        engine.dispose()


def test_clear_repository_content_ignores_alembic_cleanup_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = []
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    table = Mock()
    table.drop.side_effect = RuntimeError("drop denied")
    monkeypatch.setattr(repository_module.sa, "Table", lambda *args, **kwargs: table)
    connection = Mock()
    connection.dialect.has_schema.side_effect = RuntimeError("schema unavailable")
    engine = Mock()
    engine.connect.side_effect = lambda: nullcontext(connection)

    SARepository._clear_repository_content(engine, [], "alembic")

    table.drop.assert_called_once_with(connection, checkfirst=True)


def test_create_some_returns_ids_and_read_some_reports_missing_id(
    repo: SARepository,
) -> None:
    assert repo.create_some(RepoModel, "user", [_make_obj(1)], return_id=True) == [
        "id-1"
    ]

    with pytest.raises(exc.InvalidIdsError, match="35de72de") as error:
        repo.read_some(RepoModel, ["id-1", "missing"])

    assert error.value.ids is None
    assert "missing" in str(error.value)


def test_read_fields_rejects_non_sqlalchemy_unit_of_work(repo: SARepository) -> None:
    with pytest.raises(exc.RepositoryServiceError, match="4afb32de"):
        repo.read_fields(cast(Any, object()), "user", RepoModel, ["value"])


def test_get_where_clause_rejects_unmapped_filter_key(repo: SARepository) -> None:
    mapper = repo.get_mapper(RepoModel)

    with pytest.raises(exc.InvalidArgumentsError, match="320f2bf7"):
        repo.get_where_clause_from_filter(
            mapper.row_class,
            mapper,
            EqualsNumberFilter(key="unknown", value=1),
        )


def test_get_where_clause_converts_enum_set_members() -> None:
    class Status(Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"

    model_base = declarative_base()

    class EnumRow(model_base):
        __tablename__ = "enum_row"
        id = sa.Column(sa.Integer, primary_key=True)
        status = sa.Column(sa.Enum(Status))

    where_clause = SARepository._get_set_where_clause(
        StringSetFilter(key="status", members=frozenset({"active"})),
        EnumRow.status,
        invert=False,
    )

    assert "enum_row.status IN" in str(where_clause)


def test_verify_valid_ids_can_skip_both_checks(repo: SARepository) -> None:
    with repo.uow() as uow:
        repo.verify_valid_ids(
            uow,
            "user",
            RepoModel,
            ["duplicate", "duplicate"],
            verify_exists=False,
            verify_duplicate=False,
        )


def test_create_sqlite_engine_rejects_multiple_file_schemas(tmp_path: Path) -> None:
    sqlite_file = tmp_path / "multiple_schemas.sqlite"
    sqlite_file.touch()

    with pytest.raises(NotImplementedError, match="Multiple schemas"):
        SARepository._create_sqlite_engine(
            f"sqlite:///{sqlite_file.as_posix()}",
            {"first", "second"},
            echo=False,
            recreate_sqlite_file=False,
        )


def test_create_some_returns_empty_for_empty_iterable(repo: SARepository) -> None:
    assert repo.create_some(RepoModel, "user", iter(())) == []


def test_read_all_object_filter_preserves_ids_when_all_rows_match(
    repo: SARepository,
) -> None:
    repo.create_some(RepoModel, "user", [_make_obj(1), _make_obj(2)])

    ids = repo.read_all(
        RepoModel,
        filter=None,
        return_id=True,
        obj_filter=NumberRangeFilter(key="value", lower_bound=0),
    )

    assert ids == ["id-1", "id-2"]


@pytest.mark.parametrize("operator", [LogicalOperator.AND, LogicalOperator.OR])
def test_composite_where_clause_supports_both_operators(
    repo: SARepository, operator: LogicalOperator
) -> None:
    mapper = repo.get_mapper(RepoModel)
    filter_ = CompositeFilter(
        operator=operator,
        filters=[
            EqualsNumberFilter(key="value", value=1),
            EqualsNumberFilter(key="value", value=2),
        ],
        invert=True,
    )

    clause = repo.get_where_clause_from_filter(mapper.row_class, mapper, filter_)

    assert "NOT" in str(clause).upper()


def test_composite_where_clause_rejects_unknown_operator(repo: SARepository) -> None:
    mapper = repo.get_mapper(RepoModel)
    filter_ = CompositeFilter.model_construct(
        operator=Mock(value="UNKNOWN"), filters=[], invert=False
    )

    with pytest.raises(exc.InvalidArgumentsError, match="8f411a53"):
        repo.get_where_clause_from_filter(mapper.row_class, mapper, filter_)


def test_split_filter_leaves_unknown_composite_operator_in_python(
    repo: SARepository,
) -> None:
    filter_ = CompositeFilter.model_construct(
        operator=Mock(value="UNKNOWN"), filters=[], invert=False
    )

    assert repo.split_filter(RepoModel, filter_) == (None, filter_)


def test_register_mapper_rejects_duplicate_table_name(repo: SARepository) -> None:
    another_base: Any = declarative_base()

    class DuplicateTableRow(another_base):
        __tablename__ = "repo_model"
        __table_args__: ClassVar[tuple[Any, ...]] = tuple()
        id = sa.Column(sa.String, primary_key=True)
        value = sa.Column(sa.Integer, nullable=False)
        label = sa.Column(sa.String, nullable=True)

    with pytest.raises(exc.RepositoryInitializationServiceError, match="90c9edd0"):
        repo.register_mapper(SAMapper(RepoModel, DuplicateTableRow))


def test_create_unique_values_temp_table_generates_name() -> None:
    session = Mock()
    session.get_bind.return_value.dialect = MSSQLDialect()

    table = SARepository.create_unique_values_temp_table(
        session, sa.MetaData(), "value", sa.Uuid(), []
    )

    assert table.name.startswith("#")
    assert len(table.name) == 33
    session.execute.assert_called_once()
    session.flush.assert_not_called()


def test_clear_repository_content_rolls_back_failed_constraint_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = ["child"]
    inspector.get_foreign_keys.return_value = [{"name": "fk_child_parent"}]
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    connection = Mock()
    connection.dialect.name = "mssql"
    connection.begin.return_value.commit.side_effect = RuntimeError("commit failed")
    engine = Mock()
    engine.connect.side_effect = lambda: nullcontext(connection)

    with pytest.raises(RuntimeError, match="commit failed"):
        SARepository._clear_repository_content(engine, [RepoModel.ENTITY], None)

    connection.begin.return_value.rollback.assert_called_once_with()


def test_clear_repository_content_handles_schema_drop_error() -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = []
    connection = Mock()
    connection.dialect.has_schema.side_effect = RuntimeError("schema unavailable")
    engine = Mock()
    engine.connect.side_effect = lambda: nullcontext(connection)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    try:
        SARepository._clear_repository_content(
            engine, [Entity(persistable=True, schema_name="app")], None
        )
    finally:
        monkeypatch.undo()


def test_check_schema_matches_skips_non_persistable_entity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    monkeypatch.setattr(repository_module, "inspect", lambda _: Mock())
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )

    problems = SARepository.check_schema_matches(
        entities=[Entity(persistable=False)], connection_string="sqlite:///:memory:"
    )

    assert problems == []
    engine.dispose.assert_called_once_with()


def test_create_non_sqlite_engine_skips_existing_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    connection = Mock()
    connection.dialect.has_schema.return_value = True
    engine.connect.side_effect = lambda: nullcontext(connection)
    monkeypatch.setattr(
        repository_module.EngineFactory, "create_engine", lambda *args, **kwargs: engine
    )

    assert (
        SARepository._create_non_sqlite_engine(
            "postgresql://db", {"app"}, False, True, None
        )
        is engine
    )
    connection.execute.assert_not_called()


def test_get_where_clause_rejects_unsupported_filter(repo: SARepository) -> None:
    mapper = repo.get_mapper(RepoModel)
    filter_ = UnsupportedFilter(key="value")

    with pytest.raises(exc.InvalidArgumentsError, match="880a6446"):
        repo.get_where_clause_from_filter(mapper.row_class, mapper, filter_)


def test_split_filter_leaves_unsupported_mapped_filter_in_python(
    repo: SARepository,
) -> None:
    filter_ = UnsupportedFilter(key="value")

    assert repo.split_filter(RepoModel, filter_) == (None, filter_)


def test_crud_rejects_unsupported_operation(repo: SARepository) -> None:
    with repo.uow() as uow:
        with pytest.raises(NotImplementedError, match="not implemented"):
            repo.crud(
                uow,
                "user",
                RepoModel,
                cast(CrudOperation, object()),
            )


def test_read_some_rejects_partial_result_from_reader(
    repo: SARepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        SARepository,
        "_in_session_read_some",
        lambda *args, **kwargs: ([object()], ["id-1"]),
    )
    monkeypatch.setattr(repo, "from_sql", lambda *args, **kwargs: [_make_obj(1), None])

    with pytest.raises(exc.InvalidIdsError, match="b7efa0d3") as error:
        repo.read_some(RepoModel, ["id-1", "missing"])

    assert error.value.ids == ["id-1", "missing"]


def test_init_mappers_rejects_entity_without_db_model(repo: SARepository) -> None:
    entity = Entity(persistable=True, table_name="missing_model", id_field_name="id")
    entity.set_model_class(RepoModel)

    with pytest.raises(exc.RepositoryInitializationServiceError, match="d135c11c"):
        repo._init_mappers([entity], {}, Mock())


def test_register_mappers_rejects_entity_without_db_model(repo: SARepository) -> None:
    entity = Entity(persistable=True, table_name="missing_model", id_field_name="id")
    entity.set_model_class(RepoModel)

    with pytest.raises(exc.RepositoryInitializationServiceError, match="5f725f7a"):
        repo.register_mappers([entity])


def test_clear_repository_content_drops_named_schema_and_alembic_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspector = Mock()
    inspector.get_table_names.return_value = []
    monkeypatch.setattr(repository_module, "inspect", lambda _: inspector)
    table = Mock()
    monkeypatch.setattr(repository_module.sa, "Table", lambda *args, **kwargs: table)
    connection = Mock()
    connection.dialect.has_schema.return_value = True
    engine = Mock()
    engine.connect.side_effect = lambda: nullcontext(connection)

    SARepository._clear_repository_content(
        engine, [Entity(persistable=True, schema_name="app")], "alembic"
    )

    assert connection.execute.call_count == 2
    assert connection.commit.call_count >= 2
    table.drop.assert_called_once_with(connection, checkfirst=True)


def test_verify_valid_ids_accepts_generator(repo: SARepository) -> None:
    repo.create_one(RepoModel, "user", _make_obj(1))

    with repo.uow() as uow:
        repo.verify_valid_ids(uow, "user", RepoModel, (obj_id for obj_id in ["id-1"]))
