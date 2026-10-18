"""Check casedb geographic reference model validation and serialization."""

# pylint: disable=redefined-outer-name,missing-function-docstring
# Pytest fixtures are injected by parameter name; test names state the behavior.

from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model import geo

REGION_SET_ID = UUID("00000000-0000-0000-0000-000000000001")
FROM_REGION_ID = UUID("00000000-0000-0000-0000-000000000002")
TO_REGION_ID = UUID("00000000-0000-0000-0000-000000000003")


@pytest.fixture
def region_set_kwargs() -> dict[str, Any]:
    return {
        "code": "NUTS3",
        "name": "NUTS level 3",
        "region_code_as_label": False,
        "resolution": 3.0,
    }


@pytest.fixture
def region_kwargs() -> dict[str, Any]:
    return {
        "region_set_id": REGION_SET_ID,
        "code": "BE10",
        "name": "Brussels",
        "centroid_lat": 50.8,
        "centroid_lon": 4.3,
        "center_lat": 50.9,
        "center_lon": 4.4,
    }


@pytest.fixture
def relation_kwargs() -> dict[str, Any]:
    return {
        "from_region_id": FROM_REGION_ID,
        "to_region_id": TO_REGION_ID,
        "relation": enum.RegionRelationType.CONTAINS,
    }


@pytest.mark.parametrize(
    ("model_class", "table_name", "plural_name", "keys"),
    [
        (geo.RegionSet, "region_set", "region_sets", [("code",), ("name",)]),
        (
            geo.RegionSetShape,
            "region_set_shape",
            "region_set_shapes",
            [("region_set_id", "scale")],
        ),
        (geo.Region, "region", "regions", [("region_set_id", "code")]),
        (
            geo.RegionRelation,
            "region_relation",
            "region_relations",
            [("from_region_id", "to_region_id")],
        ),
    ],
    ids=["region-set", "region-set-shape", "region", "region-relation"],
)
def test_entity_metadata(
    model_class: type, table_name: str, plural_name: str, keys: list[tuple[str, ...]]
) -> None:
    entity = model_class.ENTITY

    assert entity.persistable is True
    assert entity.table_name == table_name
    assert entity.snake_case_plural_name == plural_name
    assert [key.field_names for key in entity.keys.values()] == keys


@pytest.mark.parametrize(
    ("model_class", "expected_links"),
    [
        (geo.RegionSet, []),
        (geo.RegionSetShape, [("region_set_id", geo.RegionSet, "region_set")]),
        (geo.Region, [("region_set_id", geo.RegionSet, "region_set")]),
        (
            geo.RegionRelation,
            [
                ("from_region_id", geo.Region, "from_region"),
                ("to_region_id", geo.Region, "to_region"),
            ],
        ),
    ],
    ids=["region-set", "region-set-shape", "region", "region-relation"],
)
def test_entity_links(
    model_class: type, expected_links: list[tuple[str, type, str]]
) -> None:
    links = model_class.ENTITY.links.values()

    assert [
        (x.link_field_name, x.link_model_class, x.relationship_field_name)
        for x in links
    ] == expected_links


def test_region_set_accepts_valid_values(region_set_kwargs: dict[str, Any]) -> None:
    region_set = geo.RegionSet(**region_set_kwargs)

    assert region_set.id is None
    assert region_set.code == "NUTS3"
    assert region_set.resolution == 3.0
    assert region_set.region_code_as_label is False


@pytest.mark.parametrize("resolution", [0, 0.0, -1, -0.001])
def test_region_set_rejects_non_positive_resolution(
    region_set_kwargs: dict[str, Any], resolution: float
) -> None:
    region_set_kwargs["resolution"] = resolution

    with pytest.raises(ValidationError):
        geo.RegionSet(**region_set_kwargs)


def test_region_set_accepts_smallest_positive_resolution(
    region_set_kwargs: dict[str, Any],
) -> None:
    region_set_kwargs["resolution"] = 1e-12

    assert geo.RegionSet(**region_set_kwargs).resolution == pytest.approx(1e-12)


@pytest.mark.parametrize("field", ["code", "name"])
@pytest.mark.parametrize(
    ("length", "is_valid"), [(255, True), (256, False)], ids=["at-max", "above-max"]
)
def test_region_set_string_length_boundary(
    region_set_kwargs: dict[str, Any], field: str, length: int, is_valid: bool
) -> None:
    region_set_kwargs[field] = "a" * length

    if is_valid:
        assert getattr(geo.RegionSet(**region_set_kwargs), field) == "a" * length
    else:
        with pytest.raises(ValidationError):
            geo.RegionSet(**region_set_kwargs)


@pytest.mark.parametrize(
    "missing", ["code", "name", "region_code_as_label", "resolution"]
)
def test_region_set_requires_fields(
    region_set_kwargs: dict[str, Any], missing: str
) -> None:
    del region_set_kwargs[missing]

    with pytest.raises(ValidationError):
        geo.RegionSet(**region_set_kwargs)


def test_region_set_shape_defaults_and_required_fields() -> None:
    shape = geo.RegionSetShape(region_set_id=REGION_SET_ID, scale=0.5, geo_json="{}")

    assert shape.region_set is None
    assert shape.geo_json == "{}"
    with pytest.raises(ValidationError):
        geo.RegionSetShape(region_set_id=REGION_SET_ID, scale=0.5)  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        geo.RegionSetShape(region_set_id="not-a-uuid", scale=0.5, geo_json="{}")


def test_region_set_shape_accepts_nested_region_set(
    region_set_kwargs: dict[str, Any],
) -> None:
    region_set = geo.RegionSet(**region_set_kwargs)

    shape = geo.RegionSetShape(
        region_set_id=REGION_SET_ID, region_set=region_set, scale=1, geo_json="{}"
    )

    assert shape.region_set is region_set
    assert shape.scale == 1.0


def test_region_accepts_valid_values(region_kwargs: dict[str, Any]) -> None:
    region = geo.Region(**region_kwargs)

    assert region.region_set is None
    assert region.region_set_id == REGION_SET_ID
    assert (region.centroid_lat, region.center_lon) == (50.8, 4.4)


@pytest.mark.parametrize("field", ["code", "name"])
@pytest.mark.parametrize(
    ("length", "is_valid"), [(255, True), (256, False)], ids=["at-max", "above-max"]
)
def test_region_string_length_boundary(
    region_kwargs: dict[str, Any], field: str, length: int, is_valid: bool
) -> None:
    region_kwargs[field] = "a" * length

    if is_valid:
        assert getattr(geo.Region(**region_kwargs), field) == "a" * length
    else:
        with pytest.raises(ValidationError):
            geo.Region(**region_kwargs)


@pytest.mark.parametrize(
    "missing",
    [
        "region_set_id",
        "code",
        "name",
        "centroid_lat",
        "centroid_lon",
        "center_lat",
        "center_lon",
    ],
)
def test_region_requires_fields(region_kwargs: dict[str, Any], missing: str) -> None:
    del region_kwargs[missing]

    with pytest.raises(ValidationError):
        geo.Region(**region_kwargs)


@pytest.mark.parametrize("value", ["not-a-float", None])
def test_region_rejects_invalid_coordinates(
    region_kwargs: dict[str, Any], value: Any
) -> None:
    region_kwargs["centroid_lat"] = value

    with pytest.raises(ValidationError):
        geo.Region(**region_kwargs)


@pytest.mark.parametrize(
    "relation",
    [enum.RegionRelationType.OVERLAPS_WITH, "OVERLAPS_WITH"],
    ids=["member", "string"],
)
def test_region_relation_normalizes_relation(
    relation_kwargs: dict[str, Any], relation: enum.RegionRelationType | str
) -> None:
    relation_kwargs["relation"] = relation

    result = geo.RegionRelation(**relation_kwargs)

    assert result.relation is enum.RegionRelationType.OVERLAPS_WITH


@pytest.mark.parametrize("relation", ["contains", "", " CONTAINS", "UNKNOWN", 1, None])
def test_region_relation_rejects_invalid_relation(
    relation_kwargs: dict[str, Any], relation: Any
) -> None:
    relation_kwargs["relation"] = relation

    with pytest.raises(ValidationError):
        geo.RegionRelation(**relation_kwargs)


@pytest.mark.parametrize("relation", list(enum.RegionRelationType))
def test_region_relation_serializes_relation_as_string_value(
    relation_kwargs: dict[str, Any], relation: enum.RegionRelationType
) -> None:
    relation_kwargs["relation"] = relation
    model = geo.RegionRelation(**relation_kwargs)

    assert model.model_dump()["relation"] == relation.value
    assert model.model_dump(mode="json")["relation"] == relation.value
    assert f'"relation":"{relation.value}"' in model.model_dump_json()


def test_region_relation_round_trips_through_dump(
    relation_kwargs: dict[str, Any],
) -> None:
    model = geo.RegionRelation(**relation_kwargs, id=uuid4())

    restored = geo.RegionRelation(**model.model_dump())

    assert restored == model


def test_region_relation_defaults_and_required_fields(
    relation_kwargs: dict[str, Any],
) -> None:
    model = geo.RegionRelation(**relation_kwargs)

    assert model.from_region is None
    assert model.to_region is None
    for missing in relation_kwargs:
        kwargs = {k: v for k, v in relation_kwargs.items() if k != missing}
        with pytest.raises(ValidationError):
            geo.RegionRelation(**kwargs)


def test_region_relation_accepts_nested_regions(
    region_kwargs: dict[str, Any], relation_kwargs: dict[str, Any]
) -> None:
    region = geo.Region(**region_kwargs)

    model = geo.RegionRelation(**relation_kwargs, from_region=region, to_region=region)

    assert model.from_region is region
    assert model.to_region is region


def test_models_do_not_share_state_between_instances(
    region_set_kwargs: dict[str, Any],
) -> None:
    first = geo.RegionSet(**region_set_kwargs)
    second = geo.RegionSet(**region_set_kwargs)

    first.name = "changed"

    assert second.name == "NUTS level 3"
    assert first.ENTITY is second.ENTITY
