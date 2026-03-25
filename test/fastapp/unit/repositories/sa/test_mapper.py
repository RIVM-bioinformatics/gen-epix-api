from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Any, Callable, ClassVar
from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import FieldType, FieldTypeSet
from gen_epix.fastapp.exc import RepositoryServiceError
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import BaseSAMapper, SAMapper


class _TableColumns:
    def __init__(self, names: Iterable[str]):
        self._names: list[str] = list(names)

    def keys(self) -> list[str]:
        return list(self._names)


class _Table:
    def __init__(self, column_names: Iterable[str]):
        self.columns: _TableColumns = _TableColumns(column_names)


class _RowBase:
    __tablename__: ClassVar[str] = "test_table"
    __table_args__: ClassVar[tuple[Any, ...]] = tuple()

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


class _Model(Model):
    id: Hashable | None = None
    link: Hashable | None = None
    value: str | None = None
    relation: list[str] | None = None


def _make_entity(*, persistable: bool = True) -> Entity:
    entity = Entity(
        persistable=persistable,
        id_field_name="id" if persistable else None,
        links={1: ("link", _Model, "relation")},  # type: ignore[dict-item]
    )
    entity.set_model_class(_Model)
    return entity


def _make_row_class(
    *,
    columns: Iterable[str],
    schema: str | None = None,
    class_attrs: dict[str, Any] | None = None,
) -> type[_RowBase]:
    attrs: dict[str, Any] = {
        "__tablename__": "test_table",
        "__table__": _Table(columns),
        "__table_args__": ({"schema": schema},) if schema else tuple(),
    }
    if class_attrs:
        attrs.update(class_attrs)
    return type("Row", (_RowBase,), attrs)


def _make_mapper(
    *,
    row_columns: Iterable[str],
    field_name_map: dict[str, str] | None = None,
    service_metadata: tuple[str, ...] | None = None,
    db_metadata: tuple[str, ...] | None = None,
    schema: str | None = None,
    generate_service: Callable[[Model, Hashable], dict[str, Any]] | None = None,
) -> tuple[SAMapper, type[_RowBase]]:
    entity = _make_entity()
    model_class = type("MyModel", (_Model,), {"ENTITY": entity})
    row_class = _make_row_class(columns=row_columns, schema=schema)
    mapper = SAMapper(
        model_class=model_class,
        row_class=row_class,
        field_name_map=field_name_map,
        service_metadata_field_names=service_metadata,
        db_metadata_field_names=db_metadata,
        generate_service_metadata=generate_service,
    )
    return mapper, row_class


class BaseMapperTestCase(TestCase):
    """Base fixtures and helpers for mapper tests."""

    def setUp(self) -> None:
        self.entity: Entity = _make_entity()
        self.model_class: type[_Model] = type(
            "TModel", (_Model,), {"ENTITY": self.entity}
        )

    def create_row(
        self,
        columns: Iterable[str],
        schema: str | None = None,
        class_attrs: dict[str, Any] | None = None,
    ) -> type[_RowBase]:
        return _make_row_class(columns=columns, schema=schema, class_attrs=class_attrs)


class _DummyMapper(BaseSAMapper):
    def __init__(self, model_class: type[Model], row_class: type[_RowBase]) -> None:
        super().__init__(model_class, row_class)  # type: ignore[arg-type]
        self._by_type: dict[FieldType, tuple[str, ...]] = {
            FieldType.ID: ("id",),
            FieldType.LINK: ("link",),
            FieldType.VALUE: ("value",),
            FieldType.RELATIONSHIP: ("relation",),
            FieldType.SERVICE_METADATA: tuple(),
            FieldType.DB_METADATA: tuple(),
            FieldType.COMPUTED: tuple(),
        }
        self._row_by_type: dict[FieldType, tuple[str, ...]] = {
            FieldType.ID: ("id_col",),
            FieldType.LINK: ("link_col",),
            FieldType.VALUE: ("value_col",),
            FieldType.RELATIONSHIP: ("relation_col",),
            FieldType.SERVICE_METADATA: tuple(),
            FieldType.DB_METADATA: tuple(),
            FieldType.COMPUTED: tuple(),
        }

    def get_field_names_by_type(self, field_type: FieldType) -> tuple[str, ...]:
        return self._by_type[field_type]

    def get_field_names_by_set(self, field_type_set: FieldTypeSet) -> tuple[str, ...]:
        names: list[str] = []
        for ft in field_type_set.value:
            names.extend(self._by_type[ft])
        return tuple(names)

    def get_row_field_names_by_type(self, field_type: FieldType) -> tuple[str, ...]:
        return self._row_by_type[field_type]

    def get_row_field_names_by_set(
        self, field_type_set: FieldTypeSet
    ) -> tuple[str, ...]:
        names: list[str] = []
        for ft in field_type_set.value:
            names.extend(self._row_by_type[ft])
        return tuple(names)

    def get_id(self, obj: Model) -> Hashable:
        return getattr(obj, "id")  # type: ignore[no-any-return]

    def get_row_id(self, row: Any) -> Hashable:
        return getattr(row, "id_col")  # type: ignore[no-any-return]

    def generate_service_metadata(
        self, obj: Model, user_id: Hashable
    ) -> dict[str, Any]:
        raise NotImplementedError()

    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        return {}

    # TODO 2953: This is a dummy method since the actual update logic is now handled by
    # the CommondbSAMapper(SAMapper) and we want to test that logic in the mapper tests,
    #  but we need to have an implementation here to satisfy the abstract method
    # requirement of BaseSAMapper.
    def update(self, user_id, obj, row, **kwargs):
        return True

    def load(self, row: Any, **kwargs: Any) -> Model:
        return _Model()

    def get_mapped_field_name(
        self, field_name: str, reverse: bool = False
    ) -> str | None:
        return super().get_mapped_field_name(field_name, reverse)


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestBaseSAMapper(BaseMapperTestCase):
    def test_init_requires_entity(self) -> None:
        # 1. Input
        row_class: type[_RowBase] = self.create_row(["id_col", "link_col", "value_col"])
        model_class: type[Model] = type("NoEntityModel", (Model,), {"ENTITY": None})

        # 2. Mocks (none)

        # 3. Execute
        with pytest.raises(RepositoryServiceError):
            _DummyMapper(model_class, row_class)

        # 4. Verify

    def test_field_name_map_and_mapped_name(self) -> None:
        # 1. Input
        row_class: type[_RowBase] = self.create_row(
            ["id_col", "link_col", "value_col", "relation_col"]
        )  # relation present
        model_class: type[_Model] = self.model_class

        # 2. Mocks (none)

        # 3. Execute
        mapper = _DummyMapper(model_class, row_class)
        forward: dict[str, str] = mapper.get_field_name_map()
        reverse: dict[str, str] = mapper.get_field_name_map(reverse=True)

        # 4. Verify
        assert forward == {
            "id": "id_col",
            "link": "link_col",
            "value": "value_col",
            "relation": "relation_col",
        }
        assert reverse == {v: k for k, v in forward.items()}
        assert mapper.get_mapped_field_name("link") == "link_col"
        assert mapper.get_mapped_field_name("link_col", reverse=True) == "link"

    def test_schema_name_property(self) -> None:
        # 1. Input
        row_with_schema: type[_RowBase] = self.create_row(
            ["id", "link", "value"], schema="myschema"
        )
        row_without_schema: type[_RowBase] = self.create_row(
            ["id", "link", "value"], schema=None
        )

        # 2. Mocks (none)

        # 3. Execute
        mapper_with, mapper_without = _DummyMapper(
            self.model_class, row_with_schema
        ), _DummyMapper(self.model_class, row_without_schema)

        # 4. Verify
        assert mapper_with.schema_name == "myschema"
        assert mapper_without.schema_name is None


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestSAMapper(BaseMapperTestCase):
    def test_identical_common_field_names_dump_load_and_maps(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "svc_a", "db_a"]
        gen_meta: Callable[[Model, Hashable], dict[str, Any]] = lambda obj, uid: {
            "svc_a": "meta",
            "added": 1,
        }

        # 2. Mocks (none)

        # 3. Execute
        mapper, row_class = _make_mapper(
            row_columns=columns,
            service_metadata=tuple(),  # explicitly service meta empty
            db_metadata=(
                "svc_a",
                "db_a",
            ),  # db_metadata must cover the extras; svc_a goes to db here
            generate_service=gen_meta,
        )

        model_obj: _Model = self.model_class(id=1, link=2, value="v", relation=["x"])
        row_obj = mapper.dump(user_id=uuid4(), obj=model_obj, extra=3)
        loaded_obj = mapper.load(row_obj, extra_loaded=True)

        # 4. Verify
        assert mapper.get_field_name_map() == {
            "id": "id",
            "link": "link",
            "value": "value",
        }
        assert mapper.get_field_name_map(reverse=True) == {
            "id": "id",
            "link": "link",
            "value": "value",
        }
        assert mapper.get_mapped_field_name("value") == "value"
        assert mapper.get_row_field_names_by_set(FieldTypeSet.DB_MODEL)[:3] == (
            "id",
            "link",
            "value",
        )
        assert getattr(row_obj, "id") == 1
        assert getattr(row_obj, "link") == 2
        assert getattr(row_obj, "value") == "v"
        assert getattr(row_obj, "extra") == 3
        assert isinstance(loaded_obj, _Model)
        assert loaded_obj.id == 1 and loaded_obj.link == 2 and loaded_obj.value == "v"

    def test_nonidentical_field_names_mapping_dump_load(self) -> None:
        # 1. Input
        field_map: dict[str, str] = {
            "id": "id_col",
            "link": "link_col",
            "value": "value_col",
            "relation": "rel_col",
        }
        columns: list[str] = [
            "id_col",
            "link_col",
            "value_col",
            "svc1",
            "db1",
        ]

        # 2. Mocks (none)

        # 3. Execute
        mapper, row_class = _make_mapper(
            row_columns=columns,
            field_name_map=field_map,
            service_metadata=("svc1",),
            db_metadata=("db1",),
        )

        model_obj: _Model = self.model_class(
            id=10, link=None, value="keep", relation=None
        )
        row_obj = mapper.dump(user_id=None, obj=model_obj)
        # For load(), construct a row that has all mapped attributes present
        row_obj_for_load = row_class(id_col=10, link_col=None, value_col="keep")
        loaded_obj = mapper.load(row_obj_for_load)  # type: ignore[arg-type]

        # 4. Verify
        assert mapper.get_field_name_map() == {
            "id": "id_col",
            "link": "link_col",
            "value": "value_col",
        }
        assert mapper.get_field_name_map(reverse=True)["value_col"] == "value"
        assert mapper.get_mapped_field_name("link") == "link_col"
        assert mapper.get_mapped_field_name("link_col", reverse=True) == "link"
        # None link should be excluded from dump; others present
        assert hasattr(row_obj, "id_col") and getattr(row_obj, "id_col") == 10
        assert not hasattr(row_obj, "link_col")
        assert getattr(row_obj, "value_col") == "keep"
        assert (
            isinstance(loaded_obj, _Model)
            and loaded_obj.value == "keep"
            and loaded_obj.id == 10
            and loaded_obj.link is None
        )

    def test_row_metadata_defaults_and_sets(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "svc_meta", "db_meta"]

        # 2. Mocks (none)

        # 3. Execute
        mapper, _ = _make_mapper(row_columns=columns)

        # 4. Verify
        assert mapper.get_row_field_names_by_type(FieldType.SERVICE_METADATA) == tuple()
        assert set(mapper.get_row_field_names_by_type(FieldType.DB_METADATA)) == {
            "svc_meta",
            "db_meta",
        }
        db_model_fields = mapper.get_row_field_names_by_set(FieldTypeSet.DB_MODEL)
        assert db_model_fields[:3] == ("id", "link", "value")

    def test_row_metadata_both_provided_success(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "only_service", "only_db"]

        # 2. Mocks (none)

        # 3. Execute
        mapper, _ = _make_mapper(
            row_columns=columns,
            service_metadata=("only_service",),
            db_metadata=("only_db",),
        )

        # 4. Verify
        assert mapper.get_row_field_names_by_type(FieldType.SERVICE_METADATA) == (
            "only_service",
        )
        assert mapper.get_row_field_names_by_type(FieldType.DB_METADATA) == ("only_db",)

    def test_row_metadata_invalid_name_raises(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "svc1", "db1"]

        # 2. Mocks (none)

        # 3. Execute / 4. Verify
        with pytest.raises(RepositoryServiceError):
            _make_mapper(
                row_columns=columns, service_metadata=("missing",), db_metadata=None
            )

    def test_row_metadata_overlap_raises(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "m", "n"]

        # 2. Mocks (none)

        # 3. Execute / 4. Verify
        with pytest.raises(RepositoryServiceError):
            _make_mapper(
                row_columns=columns, service_metadata=("m",), db_metadata=("m", "n")
            )

    def test_row_metadata_partial_coverage_raises(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "x", "y", "z"]

        # 2. Mocks (none)

        # 3. Execute / 4. Verify
        with pytest.raises(RepositoryServiceError):
            _make_mapper(
                row_columns=columns, service_metadata=("x",), db_metadata=("y",)
            )

    def test_invalid_row_field_names_raise(self) -> None:
        # 1. Input
        field_map: dict[str, str] = {
            "id": "id_col",
            "link": "missing_col",
            "value": "value_col",
        }
        columns: list[str] = ["id_col", "value_col"]  # link mapped to non-existent

        # 2. Mocks (none)

        # 3. Execute / 4. Verify
        with pytest.raises(RepositoryServiceError):
            _make_mapper(row_columns=columns, field_name_map=field_map)

    def test_get_id_and_get_row_id(self) -> None:
        # 1. Input
        field_map: dict[str, str] = {
            "id": "id_col",
            "link": "link_col",
            "value": "value_col",
        }
        columns: list[str] = ["id_col", "link_col", "value_col"]
        mapper, row_class = _make_mapper(row_columns=columns, field_name_map=field_map)
        setattr(
            row_class, "id_col", "CLASS_ID_COL"
        )  # class-level attr for class retrieval
        model_obj: _Model = self.model_class(id=123, link=0, value=None)
        row_obj = row_class(id_col=123, link_col=0, value_col=None)

        # 2. Mocks (none)

        # 3. Execute
        model_id = mapper.get_id(model_obj)
        row_id_instance = mapper.get_row_id(row_obj)
        row_id_class = mapper.get_row_id(row_class)

        # 4. Verify
        assert model_id == 123
        assert row_id_instance == 123
        assert row_id_class == "CLASS_ID_COL"

    def test_dump_merges_service_metadata_and_kwargs(self) -> None:
        # 1. Input
        field_map: dict[str, str] = {
            "id": "id_col",
            "link": "link_col",
            "value": "value_col",
        }
        columns: list[str] = ["id_col", "link_col", "value_col", "svc1", "db1"]
        gen_meta: Callable[[Model, Hashable], dict[str, Any]] = lambda obj, uid: {
            "svc1": "svc",
            "override": "svc",
        }

        # 2. Mocks (none)

        # 3. Execute
        mapper, row_class = _make_mapper(
            row_columns=columns,
            field_name_map=field_map,
            service_metadata=("svc1",),
            db_metadata=("db1",),
            generate_service=gen_meta,
        )

        model_obj: _Model = self.model_class(id=1, link=2, value="v")
        row_obj = mapper.dump(user_id=uuid4(), obj=model_obj, override="kwarg")

        # 4. Verify
        assert (
            getattr(row_obj, "override") == "kwarg"
        )  # kwargs override service metadata
        assert getattr(row_obj, "svc1") == "svc"
        assert getattr(row_obj, "db1", None) is None
