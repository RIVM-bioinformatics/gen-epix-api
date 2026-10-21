"""Validate OMOP metadata-model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.metadata import Metadata


def test_metadata_concept_id_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        Metadata.model_json_schema()["properties"]["metadata_concept_id"]["description"]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
