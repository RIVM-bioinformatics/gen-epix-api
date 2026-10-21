"""Validate OMOP ontology-model schema descriptions."""

from gen_epix.omopdb.domain.model.omop.ontology import ConceptRelationship


def test_concept_relationship_id_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        ConceptRelationship.model_json_schema()["properties"]["concept_id_1"][
            "description"
        ]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )
