"""Validate OMOP health-system model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.health_system import Location


def test_city_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        Location.model_json_schema()["properties"]["city"]["description"]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
