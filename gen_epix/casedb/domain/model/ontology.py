# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import json
from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class ConceptSet(Model):
    """
    A set of concepts in the ontology.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="concept_sets",
        table_name="concept_set",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    code: str = Field(description="The code of the concept set", max_length=255)
    name: str = Field(description="The name of the concept set", max_length=255)
    type: enum.ConceptSetType = Field(description="The type of the concept set")
    description: str | None = Field(
        default=None,
        description="The description of the concept set.",
        max_length=1000,
    )

    @field_validator("type", mode="before")
    @classmethod
    def _validate_type(cls, value: Any) -> enum.ConceptSetType:
        if isinstance(value, str):
            return enum.ConceptSetType(value)
        return value

    @field_serializer("type", mode="plain")
    def _serialize_type(self, value: enum.ConceptSetType) -> str:
        return value.value


class Concept(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="concepts",
        table_name="concept",
        persistable=True,
        keys=create_keys({1: ("concept_set_id", "code")}),
        links=create_links({1: ("concept_set_id", ConceptSet, "concept_set")}),
    )
    concept_set_id: UUID = Field(description="The ID of the concept set. FOREIGN KEY")
    concept_set: ConceptSet | None = Field(default=None, description="The concept set.")
    code: str = Field(description="Concept code within the set", max_length=255)
    name: str | None = Field(
        default=None, description="The name of the concept.", max_length=255
    )
    description: str | None = Field(
        default=None,
        description="The description of the concept.",
        max_length=1000,
    )
    rank: int | None = Field(
        default=None,
        description="The rank of the concept within the set. Must be provided for ordinal sets, for other sets it is optional and can be used for sorting.",
    )
    props: dict[str, Any] | None = Field(
        default=None, description="Additional properties of the concept."
    )

    @field_validator("props", mode="before")
    @classmethod
    def _validate_props(cls, value: dict[str, Any]) -> dict[str, Any]:
        if isinstance(value, str):
            # Assume json
            return json.loads(value)
        return value

    @field_serializer("props", mode="plain")
    def _serialize_props(self, value: dict[str, Any] | None) -> str | None:
        if value is None:
            return None
        return json.dumps(value)


class ConceptRelation(Model):
    """
    A relation between two concepts (analogous to RegionRelation).
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="concept_relations",
        table_name="concept_relation",
        persistable=True,
        keys=create_keys({1: ("from_concept_id", "to_concept_id")}),
        links=create_links(
            {
                1: ("from_concept_id", Concept, "from_concept"),
                2: ("to_concept_id", Concept, "to_concept"),
            }
        ),
    )
    from_concept_id: UUID = Field(
        description="The ID of the first concept. FOREIGN KEY"
    )
    from_concept: Concept | None = Field(default=None, description="The first concept.")
    to_concept_id: UUID = Field(description="The ID of the second concept. FOREIGN KEY")
    to_concept: Concept | None = Field(default=None, description="The second concept.")
    relation: enum.ConceptRelationType = Field(
        description="The relation between the two concepts."
    )

    @field_validator("relation")
    @classmethod
    def _validate_relation(
        cls, value: enum.ConceptRelationType | str
    ) -> enum.ConceptRelationType:
        if isinstance(value, str):
            value = enum.ConceptRelationType(value)
        return value

    @field_serializer("relation", mode="plain")
    def _serialize_relation(self, value: enum.ConceptRelationType) -> str:
        return value.value


class Disease(Model):
    """
    A disease.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="diseases",
        table_name="disease",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    name: str = Field(description="The name of the disease", max_length=255)
    icd_code: str | None = Field(
        default=None,
        description="The ICD code of the disease, if available",
        max_length=255,
    )


class EtiologicalAgent(Model):
    """
    An etiological agent.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="etiological_agents",
        table_name="etiological_agent",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    name: str = Field(description="The name of the etiological agent", max_length=255)
    type: str = Field(description="The type of the etiological agent", max_length=255)


class Etiology(Model):
    """
    The etiology of a disease based on an etiological agent.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="etiologies",
        table_name="etiology",
        persistable=True,
        keys=create_keys({1: ("disease_id", "etiological_agent_id")}),
        links=create_links(
            {
                1: ("disease_id", Disease, "disease"),
                2: ("etiological_agent_id", EtiologicalAgent, "etiological_agent"),
            }
        ),
    )
    disease_id: UUID = Field(description="The ID of the disease. FOREIGN KEY")
    disease: Disease | None = Field(default=None, description="The disease")
    etiological_agent_id: UUID = Field(
        description="The ID of the etiological agent. FOREIGN KEY"
    )
    etiological_agent: EtiologicalAgent | None = Field(
        None, description="The etiological agent"
    )
