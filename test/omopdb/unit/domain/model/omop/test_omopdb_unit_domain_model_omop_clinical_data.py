"""Validate OMOP clinical-data model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.clinical_data import Death


def test_person_id_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        Death.model_json_schema()["properties"]["person_id"]["description"]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
