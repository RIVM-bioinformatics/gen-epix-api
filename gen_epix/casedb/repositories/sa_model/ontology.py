# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Any
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.ONTOLOGY.value)


class ConceptSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.ConceptSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.ConceptSet, "name")
    type: Mapped[enum.ConceptSetType] = create_mapped_column(
        DOMAIN, model.ConceptSet, "type"
    )
    regex: Mapped[str] = create_mapped_column(DOMAIN, model.ConceptSet, "regex")
    schema_definition: Mapped[str] = create_mapped_column(
        DOMAIN, model.ConceptSet, "schema_definition"
    )
    schema_uri: Mapped[str] = create_mapped_column(
        DOMAIN, model.ConceptSet, "schema_uri"
    )
    description: Mapped[str] = create_mapped_column(
        DOMAIN, model.ConceptSet, "description"
    )


class Concept(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Concept)

    concept_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Concept, "concept_set_id"
    )

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Concept, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Concept, "name")
    description: Mapped[str] = create_mapped_column(
        DOMAIN, model.Concept, "description"
    )
    rank: Mapped[int] = create_mapped_column(DOMAIN, model.Concept, "rank")
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.Concept, "props")


class ConceptRelation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptRelation)

    from_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelation, "from_concept_id"
    )
    to_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelation, "to_concept_id"
    )
    relation: Mapped[enum.ConceptRelationType] = create_mapped_column(
        DOMAIN, model.ConceptRelation, "relation"
    )


class Disease(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Disease)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.Disease, "name")
    icd_code: Mapped[str] = create_mapped_column(DOMAIN, model.Disease, "icd_code")


class EtiologicalAgent(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.EtiologicalAgent)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.EtiologicalAgent, "name")
    type: Mapped[str] = create_mapped_column(DOMAIN, model.EtiologicalAgent, "type")


class Etiology(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Etiology)

    disease_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Etiology, "disease_id"
    )
    etiological_agent_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Etiology, "etiological_agent_id"
    )

    disease: Mapped[Disease] = relationship(Disease, foreign_keys=[disease_id])
    etiological_agent: Mapped[EtiologicalAgent] = relationship(
        EtiologicalAgent, foreign_keys=[etiological_agent_id]
    )
