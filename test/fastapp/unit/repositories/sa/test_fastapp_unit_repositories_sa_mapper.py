from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Any, Callable, ClassVar
from uuid import uuid4

import pytest
import sqlalchemy as sa
from pydantic import computed_field

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import FieldType, FieldTypeSet
from gen_epix.fastapp.exc import RepositoryServiceError
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.mapper import (
    BaseSAMapper,
    BaseSAMapperFactory,
    SAMapper,
    SAMapperFactory,
)


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
    column_names = list(columns)
    if not column_names:
        column_names = ["id"]

    metadata = sa.MetaData()
    table = sa.Table(
        "test_table",
        metadata,
        *(sa.Column(col_name, sa.String()) for col_name in column_names),
        schema=schema,
    )

    attrs: dict[str, Any] = {
        "__tablename__": "test_table",
        "__table__": table,
        "__table_args__": ({"schema": schema},) if schema else tuple(),
    }
    for col_name in column_names:
        attrs[col_name] = table.c[col_name]
    if class_attrs:
        attrs.update(class_attrs)
    return type("Row", (_RowBase,), attrs)


def _make_mapper(
    *,
    row_columns: Iterable[str],
    field_name_map: dict[str, str] | None = None,
    schema: str | None = None,
) -> tuple[SAMapper, type[_RowBase]]:
    entity = _make_entity()
    model_class = type("MyModel", (_Model,), {"ENTITY": entity})
    row_class = _make_row_class(columns=row_columns, schema=schema)
    mapper = SAMapper(
        model_class=model_class,
        row_class=row_class,
        field_name_map=field_name_map,
    )
    return mapper, row_class


class BaseMapperTestCase:
    """Base fixtures and helpers for mapper tests."""

    def setup_method(self) -> None:
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
        for field_type in field_type_set.value:
            names.extend(self._by_type[field_type])
        return tuple(names)

    def get_row_field_names_by_type(self, field_type: FieldType) -> tuple[str, ...]:
        return self._row_by_type[field_type]

    def get_row_field_names_by_set(
        self, field_type_set: FieldTypeSet
    ) -> tuple[str, ...]:
        names: list[str] = []
        for field_type in field_type_set.value:
            names.extend(self._row_by_type[field_type])
        return tuple(names)

    def get_id(self, obj: Model) -> Hashable:
        return getattr(obj, "id")  # type: ignore[no-any-return]

    def get_row_id(self, row: Any) -> Hashable:
        return getattr(row, "id_col")  # type: ignore[no-any-return]

    def get_row_id_column(self):
        return self.row_class.__table__.c.id_col

    def generate_service_metadata(
        self, obj: Model, user_id: Hashable
    ) -> dict[str, Any]:
        raise NotImplementedError()

    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        return {}

    # This is a dummy method since the actual update logic is now handled by
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
        assert reverse == {y: x for x, y in forward.items()}
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
        assert mapper_with.table_name == "test_table"
        assert mapper_with.model_class is self.model_class
        assert mapper_with.row_class is row_with_schema

    def test_schema_name_from_direct_table_args_dict(self) -> None:
        row_class = self.create_row(
            ["id", "link", "value"],
            class_attrs={"__table_args__": {"schema": "myschema"}},
        )

        mapper = _DummyMapper(self.model_class, row_class)

        assert mapper.schema_name == "myschema"


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestSAMapper(BaseMapperTestCase):
    def test_factory_and_field_name_accessors(self) -> None:
        row_class = self.create_row(["id", "link", "value"])
        mapper = SAMapperFactory().create_mapper(self.model_class, row_class)

        assert isinstance(mapper, SAMapper)
        assert mapper.get_field_names_by_type(FieldType.VALUE) == ("value",)
        assert mapper.get_field_names_by_set(FieldTypeSet.MODEL_DB_COMMON) == (
            "id",
            "link",
            "value",
        )
        assert mapper.get_row_field_names_by_type(FieldType.VALUE) == ("value",)
        assert mapper.get_row_field_names_by_set(FieldTypeSet.MODEL_DB_COMMON) == (
            "id",
            "link",
            "value",
        )
        assert mapper.get_mapped_field_name("link", reverse=True) == "link"
        assert mapper.get_row_id_column() is row_class.id

    def test_retrieve_and_validate_row_only_fields(self) -> None:
        mapper, row_class = _make_mapper(
            row_columns=["id", "link", "value", "created_at", "updated_at"]
        )

        assert mapper._retrieve_field_names(
            row_class, ("created_at",), ["updated_at"]
        ) == (
            ("created_at",),
            ("updated_at",),
            ["created_at", "updated_at"],
            {"created_at", "updated_at"},
        )
        assert mapper._retrieve_field_names(row_class) == (
            None,
            None,
            ["created_at", "updated_at"],
            {"created_at", "updated_at"},
        )

        with pytest.raises(RepositoryServiceError):
            mapper._retrieve_field_names(
                row_class, service_metadata_field_names=("missing",)
            )
        with pytest.raises(RepositoryServiceError):
            mapper._check_field_names(
                row_class, 1, "field_names", {"created_at"}  # type: ignore[arg-type]
            )

    def test_relationship_fields_map_only_when_row_attribute_exists(self) -> None:
        entity = _make_entity()
        model_class = type("RelationshipModel", (_Model,), {"ENTITY": entity})
        row_class = _make_row_class(
            columns=["id", "link", "value"],
            class_attrs={"relationship_row": object()},
        )

        mapper = SAMapper(
            model_class,
            row_class,
            field_name_map={"relation": "relationship_row"},
        )

        assert mapper._relationship_field_name_map == {"relation": "relationship_row"}
        assert mapper._relationship_field_name_reverse_map == {
            "relationship_row": "relation"
        }

    def test_mapper_requires_one_id_field(self) -> None:
        entity = _make_entity(persistable=False)
        model_class = type("NonPersistableModel", (_Model,), {"ENTITY": entity})
        row_class = _make_row_class(columns=["id", "link", "value"])

        with pytest.raises(NotImplementedError):
            SAMapper(model_class, row_class)

    def test_update_reports_changed_and_unchanged_rows(self) -> None:
        mapper, row_class = _make_mapper(
            row_columns=["id_col", "link_col", "value_col"],
            field_name_map={
                "id": "id_col",
                "link": "link_col",
                "value": "value_col",
            },
        )
        model_obj = mapper.model_class(id=1, link=None, value="new")
        row_obj = row_class(id_col=1, link_col=2, value_col="old")

        assert mapper.update(None, model_obj, row_obj) is True
        assert row_obj.link_col is None
        assert row_obj.value_col == "new"
        assert mapper.update(None, model_obj, row_obj) is False

    def test_identical_common_field_names_dump_load_and_maps(self) -> None:
        # 1. Input
        columns: list[str] = ["id", "link", "value", "svc_a", "db_a"]
        gen_meta: Callable[[Model, Hashable], dict[str, Any]] = lambda obj, uid: {
            "svc_a": "meta",
            "added": 1,
        }

        # 2. Mocks (none)

        # 3. Execute
        mapper, row_class = _make_mapper(row_columns=columns)

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
        assert mapper.get_mapped_field_name("missing") is None
        assert mapper.get_row_field_names_by_set(FieldTypeSet.DB_MODEL)[:3] == (
            "id",
            "link",
            "value",
        )
        assert getattr(row_obj, "id") == 1
        assert getattr(row_obj, "link") == 2
        assert getattr(row_obj, "value") == "v"
        assert "relation" not in row_obj.__dict__
        assert getattr(row_obj, "extra") == 3
        assert isinstance(loaded_obj, _Model)
        assert loaded_obj.id == 1 and loaded_obj.link == 2 and loaded_obj.value == "v"

    def test_dump_includes_computed_fields_with_matching_row_columns(self) -> None:
        entity = Entity(
            persistable=True,
            id_field_name="id",
            links={1: ("link", _Model, "relation")},  # type: ignore[dict-item]
        )

        class ComputedModel(_Model):
            @computed_field
            @property
            def computed_value(self) -> str:
                return "computed"

        entity.set_model_class(ComputedModel)
        ComputedModel.ENTITY = entity
        row_class = _make_row_class(columns=["id", "link", "value", "computed_value"])
        mapper = SAMapper(ComputedModel, row_class)

        row_obj = mapper.dump(
            user_id=None,
            obj=ComputedModel(id=1, link=2, value="value", relation=["related"]),
        )

        assert row_obj.computed_value == "computed"
        assert "relation" not in row_obj.__dict__

    def test_base_contract_methods_raise_not_implemented(self) -> None:
        row_class = self.create_row(["id_col", "link_col", "value_col"])
        mapper = _DummyMapper(self.model_class, row_class)
        model_obj = self.model_class(id=1, link=2, value="v")
        row_obj = row_class(id_col=1, link_col=2, value_col="v")

        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_field_names_by_type(mapper, FieldType.ID)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_field_names_by_set(mapper, FieldTypeSet.ID)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_row_field_names_by_type(mapper, FieldType.ID)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_row_field_names_by_set(mapper, FieldTypeSet.ID)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_row_id(mapper, row_obj)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.get_row_id_column(mapper)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.dump(mapper, None, model_obj)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.update(mapper, None, model_obj, row_obj)
        with pytest.raises(NotImplementedError):
            BaseSAMapper.load(mapper, row_obj)
        with pytest.raises(NotImplementedError):
            BaseSAMapperFactory.create_mapper(object(), self.model_class, row_class)

        assert BaseSAMapper.get_id(mapper, model_obj) == 1

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
        ]

        # 2. Mocks (none)

        # 3. Execute
        mapper, row_class = _make_mapper(
            row_columns=columns,
            field_name_map=field_map,
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
        assert "link_col" not in row_obj.__dict__
        assert getattr(row_obj, "value_col") == "keep"
        assert (
            isinstance(loaded_obj, _Model)
            and loaded_obj.value == "keep"
            and loaded_obj.id == 10
            and loaded_obj.link is None
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
