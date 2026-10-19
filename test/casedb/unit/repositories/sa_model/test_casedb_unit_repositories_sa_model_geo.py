"""Validate the casedb geographic SQLAlchemy mappings."""

import pytest
from sqlalchemy import inspect

from gen_epix.casedb.repositories.sa_model import geo as geo_sa


@pytest.mark.parametrize(
    ("mapped_model", "table_name", "columns", "nullable_columns"),
    [
        (
            geo_sa.RegionSet,
            "region_set",
            {"code", "name", "region_code_as_label", "resolution"},
            set(),
        ),
        (
            geo_sa.RegionSetShape,
            "region_set_shape",
            {"region_set_id", "scale", "geo_json"},
            set(),
        ),
        (
            geo_sa.Region,
            "region",
            {
                "region_set_id",
                "code",
                "name",
                "centroid_lat",
                "centroid_lon",
                "center_lat",
                "center_lon",
            },
            set(),
        ),
        (
            geo_sa.RegionRelation,
            "region_relation",
            {"from_region_id", "to_region_id", "relation"},
            set(),
        ),
    ],
    ids=["region-set", "region-set-shape", "region", "region-relation"],
)
def test_entity_mapping_matches_schema_contract(
    mapped_model: type,
    table_name: str,
    columns: set[str],
    nullable_columns: set[str],
) -> None:
    """Keep geographic table names, fields, and nullability aligned with domain."""
    table = mapped_model.__table__

    assert table.name == table_name
    assert columns <= set(table.columns.keys())
    assert {name for name in columns if table.c[name].nullable} == nullable_columns


@pytest.mark.parametrize(
    ("mapped_model", "field_name", "target"),
    [
        (geo_sa.RegionSetShape, "region_set_id", "geo.region_set.id"),
        (geo_sa.Region, "region_set_id", "geo.region_set.id"),
        (geo_sa.RegionRelation, "from_region_id", "geo.region.id"),
        (geo_sa.RegionRelation, "to_region_id", "geo.region.id"),
    ],
    ids=[
        "shape-region-set",
        "region-region-set",
        "relation-source",
        "relation-target",
    ],
)
def test_link_columns_reference_their_entity_ids(
    mapped_model: type, field_name: str, target: str
) -> None:
    """Map each geographic link column to its referenced entity ID."""
    column = mapped_model.__table__.c[field_name]

    assert {foreign_key.target_fullname for foreign_key in column.foreign_keys} == {
        target
    }


@pytest.mark.parametrize(
    ("mapped_model", "relationship_name", "target_model", "foreign_key_name"),
    [
        (geo_sa.RegionSetShape, "region_set", geo_sa.RegionSet, "region_set_id"),
        (geo_sa.Region, "region_set", geo_sa.RegionSet, "region_set_id"),
        (geo_sa.RegionRelation, "from_region", geo_sa.Region, "from_region_id"),
        (geo_sa.RegionRelation, "to_region", geo_sa.Region, "to_region_id"),
    ],
    ids=[
        "shape-region-set",
        "region-region-set",
        "relation-source",
        "relation-target",
    ],
)
def test_relationships_use_their_link_columns(
    mapped_model: type,
    relationship_name: str,
    target_model: type,
    foreign_key_name: str,
) -> None:
    """Tie geographic ORM relationships to the intended entity link columns."""
    relationship = inspect(mapped_model).relationships[relationship_name]

    assert relationship.mapper.class_ is target_model
    assert relationship.uselist is False
    assert relationship.local_columns == {mapped_model.__table__.c[foreign_key_name]}
