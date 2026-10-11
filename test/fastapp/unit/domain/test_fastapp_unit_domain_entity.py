"""Tests for entity metadata and relationship ordering."""

from enum import Enum
from typing import ClassVar
from uuid import UUID

import pytest
from pydantic import BaseModel, Field, computed_field

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.key import Key
from gen_epix.fastapp.domain.link import Link, MultiLink
from gen_epix.fastapp.enum import FieldType, OnException, StringCasing
from gen_epix.fastapp.exc import DomainException


class ParentModel(BaseModel):
    """Model used as a dependency in the entity-ordering test."""

    id: UUID
    NAME: ClassVar[str] = "Parent"
    ENTITY: ClassVar[Entity | None] = None


class ChildModel(BaseModel):
    """Model linked to its parent in the entity-ordering test."""

    id: UUID
    parent_id: UUID | None = None
    parent_records: list[UUID] = Field(default_factory=list)
    parents: list[UUID] = Field(default_factory=list)
    NAME: ClassVar[str] = "Child"
    ENTITY: ClassVar[Entity | None] = None


class MetadataModel(BaseModel):
    """Model with aliased, linked, and computed fields for entity tests."""

    id: UUID
    code: str = Field(alias="externalCode")
    parent_id: UUID | None = None
    parent_records: list[UUID] = Field(default_factory=list)
    NAME: ClassVar[str] = "Metadata"
    ENTITY: ClassVar[Entity | None] = None

    @computed_field
    @property
    def normalized_code(self) -> str:
        return self.code.lower()


class NameValue(Enum):
    SINGULAR = "single_value"


def test_init_sets_defaults_normalizes_names_and_converts_metadata() -> None:
    """Normalize enum names and convert key/link declarations to objects."""
    empty = Entity()
    assert empty.persistable is False
    assert empty.id_field_name is None
    assert empty.keys == {}
    assert empty.links == {}
    assert empty.multi_links == []

    entity = Entity(
        persistable=True,
        snake_case_singular_name=NameValue.SINGULAR,
        keys={1: ("code",)},
        links={1: ("parent_id", ParentModel, "parent_records")},
    )

    assert entity.id_field_name == Entity.DEFAULT_ID_FIELD_NAME
    assert entity.snake_case_singular_name == "single_value"
    assert isinstance(entity.keys[1], Key)
    assert entity.keys[1].field_names == ("code",)
    assert isinstance(entity.links[1], Link)
    assert entity.links[1].to_tuple() == (
        "parent_id",
        ParentModel,
        "parent_records",
    )


def test_entity_defaults_use_independent_mutable_values() -> None:
    """Each entity gets its own ID and metadata collections."""
    first = Entity()
    second = Entity()
    first.keys[1] = Key("code")
    first.multi_links.append(
        MultiLink(link_field_name="parents", link_model_class=ParentModel)
    )

    assert first.id != second.id
    assert second.keys == {}
    assert second.multi_links == []


@pytest.mark.parametrize(
    "attribute",
    [
        "name",
        "model_class",
        "crud_command_class",
        "db_model_class",
        "create_api_model_class",
        "read_api_model_class",
        "get_obj_id",
    ],
)
def test_model_dependent_properties_require_a_model(attribute: str) -> None:
    """Model-dependent properties reject entities without a bound model."""
    with pytest.raises(DomainException) as error:
        getattr(Entity(), attribute)

    assert error.value.message == Entity.NO_MODEL_ERROR_MSG


def test_get_keys_generator_and_field_names_require_initialized_state() -> None:
    """Helpers report uninitialized field and model state explicitly."""
    entity = Entity()

    with pytest.raises(ValueError, match="Entity does not have fields set"):
        entity.get_field_names()
    with pytest.raises(ValueError, match="Entity does not have a model set"):
        entity.get_keys_generator()


def test_set_model_class_is_idempotent_and_obeys_existing_model_policy() -> None:
    """Model binding is idempotent and supports explicit replacement."""
    entity = Entity(persistable=True)

    assert entity.set_model_class(MetadataModel) is entity
    assert entity.set_model_class(MetadataModel) is entity
    with pytest.raises(
        ValueError, match="Entity already has a model set: MetadataModel"
    ):
        entity.set_model_class(ParentModel)
    with pytest.raises(ValueError, match="Unknown on_existing value: ignore"):
        entity.set_model_class(ParentModel, on_existing="ignore")

    assert entity.set_model_class(ParentModel, on_existing="replace") is entity
    assert entity.model_class is ParentModel


@pytest.mark.parametrize(
    ("entity", "model_class", "message"),
    [
        (
            Entity(persistable=True, id_field_name="missing"),
            MetadataModel,
            "does not contain a valid field name: missing",
        ),
        (
            Entity(links={1: ("missing", MetadataModel, None)}),
            MetadataModel,
            "Link field name missing",
        ),
        (
            Entity(links={1: ("parent_id", MetadataModel, "absent_relationship")}),
            MetadataModel,
            "Back populate field name absent_relationship",
        ),
        (
            Entity(
                persistable=True,
                links={1: ("parent_id", MetadataModel, "id")},
            ),
            MetadataModel,
            "Back populate field name is identical to id field name: id",
        ),
    ],
    ids=[
        "invalid-id-field",
        "invalid-link-field",
        "invalid-relationship",
        "relationship-is-id",
    ],
)
def test_set_model_class_rejects_invalid_field_metadata(
    entity: Entity, model_class: type[BaseModel], message: str
) -> None:
    """Model registration validates identifier, link, and relationship fields."""
    with pytest.raises(ValueError, match=message):
        entity.set_model_class(model_class)


def test_set_model_class_rejects_duplicate_and_overlapping_link_fields() -> None:
    """Link and relationship names must be unique and disjoint."""
    duplicate_links = Entity(
        links={
            1: ("parent_id", ParentModel, None),
            2: ("parent_id", MetadataModel, None),
        }
    )
    with pytest.raises(ValueError, match="Link field name parent_id.*is not unique"):
        duplicate_links.set_model_class(MetadataModel)

    duplicate_relationships = Entity(
        links={
            1: ("parent_id", ParentModel, "parent_records"),
            2: ("code", MetadataModel, "parent_records"),
        }
    )
    with pytest.raises(
        ValueError, match="Back populate field name parent_records.*is not unique"
    ):
        duplicate_relationships.set_model_class(MetadataModel)

    overlapping_names = Entity(
        links={
            1: ("parent_id", ParentModel, "code"),
            2: ("code", MetadataModel, None),
        }
    )
    with pytest.raises(ValueError, match="identical to link field names: code"):
        overlapping_names.set_model_class(MetadataModel)


def test_entity_model_setters_and_properties_enforce_persistence() -> None:
    """Persistence-only classes require both a model and a persistable entity."""
    not_persistable = Entity().set_model_class(MetadataModel)
    with pytest.raises(ValueError, match=Entity.NOT_PERSISTABLE_ERROR_MSG):
        _ = not_persistable.db_model_class
    with pytest.raises(ValueError, match=Entity.NOT_PERSISTABLE_ERROR_MSG):
        _ = not_persistable.crud_command_class
    with pytest.raises(ValueError, match=Entity.NOT_PERSISTABLE_ERROR_MSG):
        not_persistable.set_db_model_class(ParentModel)
    with pytest.raises(ValueError, match=Entity.NOT_PERSISTABLE_ERROR_MSG):
        not_persistable.set_crud_command_class(ParentModel)

    entity = Entity(persistable=True).set_model_class(MetadataModel)
    assert entity.set_db_model_class(ParentModel) is entity
    assert entity.set_crud_command_class(ChildModel) is entity
    assert entity.set_create_api_model_class(ChildModel) is entity
    assert entity.set_read_api_model_class(ParentModel) is entity
    assert entity.db_model_class is ParentModel
    assert entity.crud_command_class is ChildModel
    assert entity.create_api_model_class is ChildModel
    assert entity.read_api_model_class is ParentModel


def test_model_only_setters_reject_entities_without_a_model() -> None:
    """Every model-class setter rejects an unbound entity."""
    entity = Entity()
    setters = (
        entity.set_db_model_class,
        entity.set_create_api_model_class,
        entity.set_read_api_model_class,
        entity.set_crud_command_class,
    )
    for setter in setters:
        with pytest.raises(DomainException) as error:
            setter(ParentModel)
        assert error.value.message == Entity.NO_MODEL_ERROR_MSG


def test_model_fields_are_classified_and_exposed_by_name_or_alias() -> None:
    """Model field helpers preserve aliases and filter by the derived type."""
    entity = Entity(
        persistable=True,
        keys={1: ("code",)},
        links={1: ("parent_id", ParentModel, "parent_records")},
    ).set_model_class(MetadataModel)

    assert entity.get_field_names() == [
        "id",
        "externalCode",
        "parent_id",
        "parent_records",
        "normalized_code",
    ]
    assert entity.get_field_names(by_alias=False) == [
        "id",
        "code",
        "parent_id",
        "parent_records",
        "normalized_code",
    ]
    assert entity.get_field_names(field_type=FieldType.COMPUTED) == ["normalized_code"]
    assert entity.get_id_field_name() == "id"
    assert entity.get_id_field_name(by_alias=False) == "id"
    assert entity.get_keys_field_names() == [("externalCode",)]
    assert entity.get_keys_field_names(by_alias=False) == [("code",)]
    assert entity.get_link_field_names() == ["parent_id"]
    assert entity.get_relationship_field_names() == ["parent_records"]
    assert entity.get_value_field_names() == ["externalCode"]

    instance = MetadataModel(id=UUID(int=1), externalCode="ABC")
    assert entity.get_obj_id(instance) == UUID(int=1)
    assert entity.get_keys_generator()(instance) == {1: "ABC"}


def test_entity_field_helpers_handle_models_without_ids_or_keys() -> None:
    """Optional ID and key metadata has explicit empty outcomes."""
    entity = Entity().set_model_class(ChildModel)

    assert entity.get_keys_generator()({}) == {}
    with pytest.raises(AttributeError, match="does not have an ID field"):
        entity.get_id_field_name()


def test_link_helpers_return_link_entity_properties_and_identifier_callable() -> None:
    """Link helpers expose linked entities and resolve the linked ID field."""
    parent = Entity(persistable=True).set_model_class(ParentModel)
    ParentModel.ENTITY = parent
    child = Entity(
        persistable=True,
        links={1: ("parent_id", ParentModel, "parent_records")},
    ).set_model_class(MetadataModel)

    assert child.get_link_entity("parent_id") is parent
    assert child.get_link_entity("unknown") is None
    assert child.get_link_properties_by_field_name("parent_id") == (
        1,
        ParentModel,
        "parent_records",
    )
    with pytest.raises(ValueError, match="Field unknown is not a link field"):
        child.get_link_properties_by_field_name("unknown")

    instance = MetadataModel(id=UUID(int=2), externalCode="abc", parent_id=UUID(int=3))
    assert child.get_link_id(ParentModel)(instance) == UUID(int=3)
    with pytest.raises(ValueError, match="No link or several links to ChildModel"):
        child.get_link_id(ChildModel)


def test_duplicate_links_to_one_model_have_no_unambiguous_link_id() -> None:
    """Multiple links to the same model do not expose a singular ID getter."""
    entity = Entity(
        links={
            1: ("parent_id", ParentModel, None),
            2: ("code", ParentModel, None),
        }
    ).set_model_class(MetadataModel)

    with pytest.raises(ValueError, match="No link or several links to ParentModel"):
        entity.get_link_id(ParentModel)


def test_has_metadata_methods_report_configured_collections() -> None:
    """Presence checks reflect empty and populated metadata collections."""
    entity = Entity()
    assert not entity.has_keys()
    assert not entity.has_links()
    assert not entity.has_multi_links()

    configured = Entity(
        keys={1: ("code",)},
        links={1: ("parent_id", ParentModel, None)},
        multi_links=[
            MultiLink(link_field_name="parents", link_model_class=ParentModel)
        ],
    )
    assert configured.has_keys()
    assert configured.has_links()
    assert configured.has_multi_links()


@pytest.mark.parametrize(
    ("casing", "expected"),
    [
        (StringCasing.SNAKE_CASE, "item_name"),
        (StringCasing.CAMEL_CASE, "itemName"),
        (StringCasing.PASCAL_CASE, "ItemName"),
    ],
    ids=["snake", "camel", "pascal"],
)
def test_get_name_by_casing_selects_singular_and_plural_fields(
    casing: StringCasing, expected: str
) -> None:
    """Configured naming styles return the requested grammatical form."""
    entity = Entity(
        snake_case_singular_name="item_name",
        snake_case_plural_name="item_names",
        camel_case_singular_name="itemName",
        camel_case_plural_name="itemNames",
        pascal_case_singular_name="ItemName",
        pascal_case_plural_name="ItemNames",
    )

    assert entity.get_name_by_casing(casing) == expected
    assert (
        entity.get_name_by_casing(casing, is_plural=True)
        == {
            StringCasing.SNAKE_CASE: "item_names",
            StringCasing.CAMEL_CASE: "itemNames",
            StringCasing.PASCAL_CASE: "ItemNames",
        }[casing]
    )
    assert Entity().get_name_by_casing(casing) is None


def test_get_name_by_casing_rejects_unimplemented_casing() -> None:
    """Kebab casing is explicitly unsupported by the name selector."""
    with pytest.raises(
        NotImplementedError, match="String casing StringCasing.KEBAB_CASE"
    ):
        Entity().get_name_by_casing(StringCasing.KEBAB_CASE)


def test_clone_copies_entity_metadata_and_applies_updates() -> None:
    """Cloning isolates metadata collections and applies explicit overrides."""
    source = Entity(
        persistable=True,
        snake_case_singular_name="source",
        keys={1: ("code",)},
    ).set_model_class(MetadataModel)
    source.set_db_model_class(ParentModel)

    clone = source.clone(
        update={"snake_case_singular_name": "copy", "database_name": "copy_table"}
    )

    assert clone is not source
    assert clone.snake_case_singular_name == "copy"
    assert clone.database_name == "copy_table"
    assert clone.keys == source.keys
    assert clone.keys is not source.keys
    assert clone.get_field_names() == source.get_field_names()
    assert clone.set_model_class(MetadataModel) is clone
    assert clone.db_model_class is ParentModel


def test_camel_to_snake_case_handles_word_boundaries_and_acronyms() -> None:
    """Camel conversion splits lower-to-upper and acronym-to-word boundaries."""
    assert Entity.camel_to_snake_case("camelCase") == "camel_case"
    assert Entity.camel_to_snake_case("HTTPServer") == "http_server"
    assert Entity.camel_to_snake_case("already_snake") == "already_snake"


def test_topological_sort_returns_empty_and_ignores_external_dependencies() -> None:
    """Sorting handles empty inputs and excludes dependencies outside its input."""
    assert Entity.topological_sort([], OnException.RAISE) == []

    parent = Entity(persistable=True).set_model_class(ParentModel)
    ParentModel.ENTITY = parent
    child = Entity(
        persistable=True,
        links={1: ("parent_id", ParentModel, None)},
    ).set_model_class(ChildModel)

    assert Entity.topological_sort([child], OnException.RAISE) == [child]


def test_topological_sort_includes_multilink_dependencies() -> None:
    """Multi-links order their linked entities before the dependent entity."""
    parent = Entity(persistable=True).set_model_class(ParentModel)
    ParentModel.ENTITY = parent
    child = Entity(
        persistable=True,
        multi_links=[
            MultiLink(link_field_name="parents", link_model_class=ParentModel)
        ],
    ).set_model_class(ChildModel)

    assert Entity.topological_sort([child, parent], OnException.RAISE) == [
        parent,
        child,
    ]


def test_topological_sort_cycle_raises_or_returns_partial_result() -> None:
    """Cycles raise by default and return the acyclic prefix when ignored."""

    class LeftModel(BaseModel):
        id: UUID
        right_id: UUID | None = None
        NAME: ClassVar[str] = "Left"
        ENTITY: ClassVar[Entity | None] = None

    class RightModel(BaseModel):
        id: UUID
        left_id: UUID | None = None
        NAME: ClassVar[str] = "Right"
        ENTITY: ClassVar[Entity | None] = None

    left = Entity(links={1: ("right_id", RightModel, None)}).set_model_class(LeftModel)
    right = Entity(links={1: ("left_id", LeftModel, None)}).set_model_class(RightModel)
    LeftModel.ENTITY = left
    RightModel.ENTITY = right

    with pytest.raises(DomainException, match="Cycle detected in entity links"):
        Entity.topological_sort([left, right], OnException.RAISE)
    assert Entity.topological_sort([left, right], OnException.IGNORE) == []


def test_topological_sort_places_linked_entities_before_dependents() -> None:
    """Order linked entities before entities that depend on them."""
    parent = Entity(persistable=True).set_model_class(ParentModel)
    ParentModel.ENTITY = parent
    child = Entity(
        persistable=True,
        links={1: ("parent_id", ParentModel, None)},
    ).set_model_class(ChildModel)
    ChildModel.ENTITY = child

    assert Entity.topological_sort([child, parent], OnException.RAISE) == [
        parent,
        child,
    ]
