from typing import ClassVar
from uuid import UUID

import gen_epix.casedb.domain.model.ontology as model
from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.command import CrudCommand, UpdateAssociationCommand

# Non-CRUD


class DiseaseEtiologicalAgentUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.Etiology
    LINK_FIELD_NAME1: ClassVar = "disease_id"
    LINK_FIELD_NAME2: ClassVar = "etiological_agent_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.Etiology]


# CRUD


class ConceptCrudCommand(CrudCommand):
    """Create and manage individual concepts within a concept set, including codes, labels, and ordering."""

    MODEL_CLASS: ClassVar = model.Concept


class ConceptSetCrudCommand(CrudCommand):
    """Manage controlled vocabularies and value sets (coded lists, regex/grammar-based sets) used by case variables."""

    MODEL_CLASS: ClassVar = model.ConceptSet


class ConceptRelationCrudCommand(CrudCommand):
    """Capture hierarchical or semantic relationships between concepts (e.g., parent/child, broader/narrower)."""

    MODEL_CLASS: ClassVar = model.ConceptRelation


class DiseaseCrudCommand(CrudCommand):
    """Register diseases (ICD-coded when available) to anchor case types and etiologies to specific conditions."""

    MODEL_CLASS: ClassVar = model.Disease


class EtiologicalAgentCrudCommand(CrudCommand):
    """Register etiological agents (pathogens/causative organisms) used in disease etiologies and sequencing metadata."""

    MODEL_CLASS: ClassVar = model.EtiologicalAgent


class EtiologyCrudCommand(CrudCommand):
    """Link diseases to etiological agents to define valid disease–pathogen combinations."""

    MODEL_CLASS: ClassVar = model.Etiology
