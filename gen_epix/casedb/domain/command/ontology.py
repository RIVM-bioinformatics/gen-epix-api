from typing import ClassVar
from uuid import UUID

import gen_epix.casedb.domain.model.ontology as model
from gen_epix.commondb.domain.command import CrudCommand, UpdateAssociationCommand

# Non-CRUD


class DiseaseEtiologicalAgentUpdateAssociationCommand(UpdateAssociationCommand):
    """
    Set the etiological agents for a disease by replacing existing disease–agent
    links with the provided etiologies, then return the updated list.
    """

    ASSOCIATION_CLASS: ClassVar = model.Etiology
    LINK_FIELD_NAME1: ClassVar = "disease_id"
    LINK_FIELD_NAME2: ClassVar = "etiological_agent_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.Etiology]


# CRUD


class ConceptCrudCommand(CrudCommand):
    """Manage concepts within a concept set, including codes, labels, and ordering."""

    MODEL_CLASS: ClassVar = model.Concept


class ConceptSetCrudCommand(CrudCommand):
    """Manage controlled vocabularies and value sets (coded lists, regex/grammar-based) used by case variables."""

    MODEL_CLASS: ClassVar = model.ConceptSet


class ConceptRelationCrudCommand(CrudCommand):
    """Manage hierarchical or semantic relationships between concepts (e.g., parent/child, broader/narrower)."""

    MODEL_CLASS: ClassVar = model.ConceptRelation


class DiseaseCrudCommand(CrudCommand):
    """Manage diseases (ICD-coded when available) to anchor CaseTypes and etiologies to specific conditions."""

    MODEL_CLASS: ClassVar = model.Disease


class EtiologicalAgentCrudCommand(CrudCommand):
    """Manage etiological agents (pathogens/causative organisms) used in disease etiologies and sequencing metadata."""

    MODEL_CLASS: ClassVar = model.EtiologicalAgent


class EtiologyCrudCommand(CrudCommand):
    """Manage disease–etiological agent links defining valid disease–pathogen combinations."""

    MODEL_CLASS: ClassVar = model.Etiology
