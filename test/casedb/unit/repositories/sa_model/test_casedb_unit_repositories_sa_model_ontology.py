"""Validate the casedb ontology SQLAlchemy mappings."""

import pytest
from sqlalchemy import inspect

from gen_epix.casedb.repositories.sa_model import ontology as ontology_sa


@pytest.mark.parametrize(
    ("mapped_model", "table_name", "columns", "nullable_columns"),
    [
        (
            ontology_sa.ConceptSet,
            "concept_set",
            {"code", "name", "type", "unit", "description"},
            {"unit", "description"},
        ),
        (
            ontology_sa.Concept,
            "concept",
            {"concept_set_id", "code", "name", "description", "rank", "props"},
            {"name", "description", "rank", "props"},
        ),
        (
            ontology_sa.ConceptRelation,
            "concept_relation",
            {"from_concept_id", "to_concept_id", "relation"},
            set(),
        ),
        (
            ontology_sa.Disease,
            "disease",
            {"name", "icd_code"},
            {"icd_code"},
        ),
        (
            ontology_sa.EtiologicalAgent,
            "etiological_agent",
            {"name", "type"},
            set(),
        ),
        (
            ontology_sa.Etiology,
            "etiology",
            {"disease_id", "etiological_agent_id"},
            set(),
        ),
    ],
    ids=["concept-set", "concept", "relation", "disease", "agent", "etiology"],
)
def test_entity_mapping_matches_schema_contract(
    mapped_model: type,
    table_name: str,
    columns: set[str],
    nullable_columns: set[str],
) -> None:
    """Keep entity table names, fields, and nullability aligned with the domain."""
    table = mapped_model.__table__

    assert table.name == table_name
    assert columns <= set(table.columns.keys())
    assert {name for name in columns if table.c[name].nullable} == nullable_columns


@pytest.mark.parametrize(
    ("mapped_model", "field_name", "target"),
    [
        (ontology_sa.Concept, "concept_set_id", "ontology.concept_set.id"),
        (ontology_sa.ConceptRelation, "from_concept_id", "ontology.concept.id"),
        (ontology_sa.ConceptRelation, "to_concept_id", "ontology.concept.id"),
        (ontology_sa.Etiology, "disease_id", "ontology.disease.id"),
        (
            ontology_sa.Etiology,
            "etiological_agent_id",
            "ontology.etiological_agent.id",
        ),
    ],
    ids=["concept-set", "relation-source", "relation-target", "disease", "agent"],
)
def test_link_columns_reference_their_entity_ids(
    mapped_model: type, field_name: str, target: str
) -> None:
    """Map each ontology link column to the referenced entity ID."""
    column = mapped_model.__table__.c[field_name]

    assert {foreign_key.target_fullname for foreign_key in column.foreign_keys} == {
        target
    }


@pytest.mark.parametrize(
    ("relationship_name", "target_model", "foreign_key_name"),
    [
        ("disease", ontology_sa.Disease, "disease_id"),
        (
            "etiological_agent",
            ontology_sa.EtiologicalAgent,
            "etiological_agent_id",
        ),
    ],
    ids=["disease", "agent"],
)
def test_etiology_relationships_use_their_link_columns(
    relationship_name: str, target_model: type, foreign_key_name: str
) -> None:
    """Keep etiology ORM relationships scalar and tied to their foreign keys."""
    relationship = inspect(ontology_sa.Etiology).relationships[relationship_name]

    assert relationship.mapper.class_ is target_model
    assert relationship.uselist is False
    assert relationship.local_columns == {
        ontology_sa.Etiology.__table__.c[foreign_key_name]
    }
