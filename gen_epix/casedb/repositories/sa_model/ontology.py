# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Any, Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.casedb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.ONTOLOGY.value)


class Concept(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Concept)

    abbreviation: Mapped[str] = create_mapped_column(model.Concept, "abbreviation")
    name: Mapped[str] = create_mapped_column(model.Concept, "name")
    description: Mapped[str] = create_mapped_column(model.Concept, "description")
    props: Mapped[dict[str, Any]] = create_mapped_column(model.Concept, "props")


class ConceptSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptSet)

    code: Mapped[str] = create_mapped_column(model.ConceptSet, "code")
    name: Mapped[str] = create_mapped_column(model.ConceptSet, "name")
    type: Mapped[enum.ConceptSetType] = create_mapped_column(model.ConceptSet, "type")
    regex: Mapped[str] = create_mapped_column(model.ConceptSet, "regex")
    schema_definition: Mapped[str] = create_mapped_column(
        model.ConceptSet, "schema_definition"
    )
    schema_uri: Mapped[str] = create_mapped_column(model.ConceptSet, "schema_uri")
    description: Mapped[str] = create_mapped_column(model.ConceptSet, "description")


class ConceptSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptSetMember)

    concept_set_id: Mapped[UUID] = create_mapped_column(
        model.ConceptSetMember, "concept_set_id"
    )
    concept_id: Mapped[UUID] = create_mapped_column(
        model.ConceptSetMember, "concept_id"
    )
    rank: Mapped[int] = create_mapped_column(model.ConceptSetMember, "rank")

    concept_set: Mapped[ConceptSet] = relationship(
        ConceptSet, foreign_keys=[concept_set_id]
    )
    concept: Mapped[Concept] = relationship(Concept, foreign_keys=[concept_id])


class Disease(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Disease)

    name: Mapped[str] = create_mapped_column(model.Disease, "name")
    icd_code: Mapped[str] = create_mapped_column(model.Disease, "icd_code")


class EtiologicalAgent(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.EtiologicalAgent)

    name: Mapped[str] = create_mapped_column(model.EtiologicalAgent, "name")
    type: Mapped[str] = create_mapped_column(model.EtiologicalAgent, "type")


class Etiology(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Etiology)

    disease_id: Mapped[UUID] = create_mapped_column(model.Etiology, "disease_id")
    etiological_agent_id: Mapped[UUID] = create_mapped_column(
        model.Etiology, "etiological_agent_id"
    )

    disease: Mapped[Disease] = relationship(Disease, foreign_keys=[disease_id])
    etiological_agent: Mapped[EtiologicalAgent] = relationship(
        EtiologicalAgent, foreign_keys=[etiological_agent_id]
    )
