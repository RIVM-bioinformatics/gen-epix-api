from typing import ClassVar
from uuid import UUID

import gen_epix.casedb.domain.model.ontology as model
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
    MODEL_CLASS: ClassVar = model.Concept


class ConceptSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptSet


class ConceptRelationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptRelation


class DiseaseCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Disease


class EtiologicalAgentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.EtiologicalAgent


class EtiologyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Etiology
