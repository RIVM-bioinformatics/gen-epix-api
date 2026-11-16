"""Validate OMOP ontology-model schema descriptions."""

import hashlib
from datetime import date
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.omopdb.domain.model.omop.ontology import (
    Concept,
    ConceptAncestor,
    ConceptClass,
    ConceptRelationship,
    ConceptSynonym,
    Domain,
    DrugStrength,
    Relationship,
    SourceToConceptMap,
    Vocabulary,
)
from gen_epix.util import int_to_uuid, str_to_uuid


def _composite_uuid(*parts: bytes) -> UUID:
    return UUID(hashlib.sha256(b"".join(parts)).digest()[:16].hex())


def test_concept_relationship_id_metadata_description() -> None:
    """Expose the shared guidance description in the generated JSON Schema."""
    assert (
        ConceptRelationship.model_json_schema()["properties"]["concept_id_1"][
            "description"
        ]
        == "User guidance:\nNone\nETL conventions:\nNone"
    )


def test_relationship_natural_keys_and_concept_identifier() -> None:
    relationship = Relationship(
        relationship_str_id="Maps to",
        relationship_name="Maps to",
        is_hierarchical="0",
        defines_ancestry="0",
        reverse_relationship_str_id="Mapped from",
        relationship_concept_id=42,
    )
    aliased_keys = Relationship(
        relationship_id="Maps to",
        relationship_name="Maps to",
        is_hierarchical="0",
        defines_ancestry="0",
        reverse_relationship_id="Mapped from",
        relationship_concept_id=42,
    )

    assert relationship.relationship_id == str_to_uuid("Maps to")
    assert relationship.reverse_relationship_id == str_to_uuid("Mapped from")
    assert relationship.relationship_concept_id == int_to_uuid(42)
    assert aliased_keys.relationship_id == relationship.relationship_id
    assert aliased_keys.reverse_relationship_id == relationship.reverse_relationship_id


def test_relationship_rejects_mismatched_natural_key_uuid() -> None:
    with pytest.raises(ValidationError, match="not identical"):
        Relationship(
            relationship_id=uuid4(),
            relationship_str_id="Maps to",
            relationship_name="Maps to",
            is_hierarchical="0",
            defines_ancestry="0",
            reverse_relationship_str_id="Mapped from",
            relationship_concept_id=42,
        )


def test_concept_relationship_computes_composite_id_and_skips_partial_keys() -> None:
    concept_id_1 = int_to_uuid(101)
    concept_id_2 = int_to_uuid(202)
    relationship_id = str_to_uuid("Maps to")
    record = ConceptRelationship(
        concept_id_1=101,
        concept_id_2=202,
        relationship_id="Maps to",
        valid_start_date=date(2020, 1, 1),
        valid_end_date=date(2099, 12, 31),
    )
    partial = {"concept_id_1": 101, "concept_id_2": None, "relationship_id": "Maps to"}

    assert record.concept_id_1 == concept_id_1
    assert record.concept_id_2 == concept_id_2
    assert record.relationship_id == relationship_id
    assert record.concept_relationship_id == _composite_uuid(
        concept_id_1.bytes, concept_id_2.bytes, relationship_id.bytes
    )
    assert ConceptRelationship._validate_args(partial) is partial
    assert "concept_relationship_id" not in partial
    assert ConceptRelationship._validate_args("unchanged") == "unchanged"


def test_concept_ancestor_computes_composite_id_and_skips_partial_keys() -> None:
    ancestor_id = int_to_uuid(303)
    descendant_id = int_to_uuid(404)
    record = ConceptAncestor(
        ancestor_concept_id=303,
        descendant_concept_id=404,
        min_levels_of_separation=1,
        max_levels_of_separation=3,
    )
    partial = {"ancestor_concept_id": 303, "descendant_concept_id": None}

    assert record.ancestor_concept_id == ancestor_id
    assert record.descendant_concept_id == descendant_id
    assert record.concept_ancestor_id == _composite_uuid(
        ancestor_id.bytes, descendant_id.bytes
    )
    assert ConceptAncestor._validate_args(partial) is partial
    assert "concept_ancestor_id" not in partial
    assert ConceptAncestor._validate_args(None) is None


def test_concept_synonym_computes_composite_id_and_skips_partial_keys() -> None:
    concept_id = int_to_uuid(505)
    language_id = int_to_uuid(506)
    synonym_name = "cafe\u0301"
    record = ConceptSynonym(
        concept_id=505,
        concept_synonym_name=synonym_name,
        language_concept_id=506,
    )
    partial = {
        "concept_id": 505,
        "concept_synonym_name": synonym_name,
        "language_concept_id": None,
    }

    assert record.concept_id == concept_id
    assert record.language_concept_id == language_id
    assert record.concept_synonym_id == _composite_uuid(
        concept_id.bytes, synonym_name.encode("utf-8"), language_id.bytes
    )
    assert ConceptSynonym._validate_args(partial) is partial
    assert "concept_synonym_id" not in partial
    assert ConceptSynonym._validate_args(17) == 17


def test_drug_strength_normalizes_required_and_optional_concept_ids() -> None:
    record = DrugStrength(
        drug_concept_id=601,
        ingredient_concept_id=602,
        valid_start_date=date(2020, 1, 1),
        valid_end_date=date(2099, 12, 31),
    )

    assert record.drug_concept_id == int_to_uuid(601)
    assert record.ingredient_concept_id == int_to_uuid(602)
    assert record.amount_unit_concept_id is None
    assert record.numerator_unit_concept_id is None
    assert record.denominator_unit_concept_id is None


def test_source_to_concept_map_normalizes_concept_and_vocabulary_ids() -> None:
    record = SourceToConceptMap(
        source_code="source-1",
        source_concept_id=701,
        source_vocabulary_id=702,
        target_concept_id=703,
        target_vocabulary_id=704,
        valid_start_date=date(2020, 1, 1),
        valid_end_date=date(2099, 12, 31),
    )

    assert record.source_concept_id == int_to_uuid(701)
    assert record.source_vocabulary_id == int_to_uuid(702)
    assert record.target_concept_id == int_to_uuid(703)
    assert record.target_vocabulary_id == int_to_uuid(704)


def test_core_ontology_models_normalize_natural_keys_and_references() -> None:
    vocabulary = Vocabulary(
        vocabulary_str_id="SNOMED",
        vocabulary_name="SNOMED CT",
        vocabulary_concept_id=801,
    )
    domain = Domain(
        domain_str_id="Condition",
        domain_name="Condition",
        domain_concept_id=802,
    )
    concept_class = ConceptClass(
        concept_class_str_id="Clinical Finding",
        concept_class_name="Clinical Finding",
        concept_class_concept_id=803,
    )
    concept = Concept(
        concept_int_id=804,
        concept_name="Test concept",
        domain_id="Condition",
        vocabulary_id="SNOMED",
        concept_class_id="Clinical Finding",
        concept_code="test-code",
        valid_start_date=date(2020, 1, 1),
        valid_end_date=date(2099, 12, 31),
    )

    assert vocabulary.vocabulary_id == str_to_uuid("SNOMED")
    assert vocabulary.vocabulary_concept_id == int_to_uuid(801)
    assert domain.domain_id == str_to_uuid("Condition")
    assert domain.domain_concept_id == int_to_uuid(802)
    assert concept_class.concept_class_id == str_to_uuid("Clinical Finding")
    assert concept_class.concept_class_concept_id == int_to_uuid(803)
    assert concept.concept_id == int_to_uuid(804)
    assert concept.domain_id == str_to_uuid("Condition")
    assert concept.vocabulary_id == str_to_uuid("SNOMED")
    assert concept.concept_class_id == str_to_uuid("Clinical Finding")
