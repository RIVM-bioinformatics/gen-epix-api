"""Validate OMOP health-economics model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.health_economics import Cost


def test_cost_id_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        Cost.model_json_schema()["properties"]["cost_id"]["description"]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
