"""Validate OMOP derived-model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.derived import Cohort


def test_cohort_definition_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        Cohort.model_json_schema()["properties"]["cohort_definition_id"]["description"]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
