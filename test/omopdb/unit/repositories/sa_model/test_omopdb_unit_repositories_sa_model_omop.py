"""Tests for the SQLAlchemy mappings of persistable OmopDB OMOP models."""

import inspect

import pytest
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import RelationshipProperty

from gen_epix.omopdb.domain import enum, model
from gen_epix.omopdb.repositories.sa_model import base, omop

MAPPED_CLASSES = sorted(
    (
        cls
        for _, cls in inspect.getmembers(omop, inspect.isclass)
        if cls.__module__ == omop.__name__ and hasattr(cls, "__table__")
    ),
    key=lambda cls: cls.__name__,
)
IDENTIFIER_CLASSES = [
    cls for cls in MAPPED_CLASSES if cls.__name__.endswith("Identifier")
]
LINEAGE_CLASSES = [
    cls for cls in MAPPED_CLASSES if issubclass(cls, base.DataLineageMixin)
]


def _ids(classes: list[type]) -> list[str]:
    return [cls.__name__ for cls in classes]


def _column_names(cls: type) -> set[str]:
    return {attr.key for attr in sa_inspect(cls).column_attrs}


def test_base_is_named_after_omop_service() -> None:
    """Name the declarative base after the OMOP service type."""
    assert omop.Base.__name__ == enum.ServiceType.OMOP.value
    assert len(MAPPED_CLASSES) > 0
    assert all(issubclass(cls, omop.Base) for cls in MAPPED_CLASSES)


def _relationships(cls: type) -> list[RelationshipProperty]:
    return [
        attr for attr in sa_inspect(cls).attrs if isinstance(attr, RelationshipProperty)
    ]


@pytest.mark.parametrize("cls", MAPPED_CLASSES, ids=_ids(MAPPED_CLASSES))
def test_table_name_matches_domain_model(cls: type) -> None:
    """Use the table name that the same-named domain model defines."""
    domain_model = getattr(model, cls.__name__)

    assert cls.__tablename__ == domain_model.ENTITY.table_name
    assert cls.__table__.name == domain_model.ENTITY.table_name


@pytest.mark.parametrize("cls", MAPPED_CLASSES, ids=_ids(MAPPED_CLASSES))
def test_columns_match_domain_model_fields(cls: type) -> None:
    """Map each domain field to a column, except identifier link attributes."""
    domain_model_fields = set(getattr(model, cls.__name__).model_fields)
    link_keys = {rel.key for rel in _relationships(cls)}
    columns = _column_names(cls)

    assert columns <= domain_model_fields
    assert domain_model_fields - columns <= link_keys | {"identifier_issuer"}


@pytest.mark.parametrize("cls", LINEAGE_CLASSES, ids=_ids(LINEAGE_CLASSES))
def test_lineage_classes_have_optional_lineage_columns(cls: type) -> None:
    """Provide optional provenance columns on data-lineage mappings."""
    columns = cls.__table__.c

    assert columns["provenance_id"].nullable
    assert columns["source_traceback"].nullable
    assert isinstance(columns["source_traceback"].type, sa.Unicode)
    assert columns["source_traceback"].type.length == 255


def test_non_lineage_classes_lack_lineage_columns() -> None:
    """Keep lineage columns off mappings that do not use the mixin."""
    for cls in set(MAPPED_CLASSES) - set(LINEAGE_CLASSES):
        assert "provenance_id" not in _column_names(cls), cls.__name__


@pytest.mark.parametrize("cls", IDENTIFIER_CLASSES, ids=_ids(IDENTIFIER_CLASSES))
def test_identifier_classes_link_to_their_data_class(cls: type) -> None:
    """Relate each identifier mapping to its data class via `internal_id`."""
    data_cls = getattr(omop, cls.__name__.removesuffix("Identifier"))
    relationships = _relationships(cls)

    assert len(relationships) == 1
    assert relationships[0].mapper.class_ is data_cls
    assert [col.key for col in relationships[0].local_columns] == ["internal_id"]
