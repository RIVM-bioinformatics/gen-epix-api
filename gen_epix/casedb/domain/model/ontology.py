# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class Concept(Model):
    """
    A concept in the ontology.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="concepts",
        table_name="concept",
        persistable=True,
    )
    # TODO: consider whether abbreviation (i) should renamed to code and (ii) should be a key
    abbreviation: str = Field(description="The abbreviation for the concept.")
    name: str | None = Field(
        default=None,
        description="The name of the concept.",
        max_length=255,
    )
    description: str | None = Field(
        default=None, description="The description of the concept."
    )
    props: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties of the concept."
    )


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
    regex: str | None = Field(
        default=None,
        description=(
            "The regular expression describing the concept set,"
            " in case of type REGULAR_EXPRESSION"
        ),
    )
    schema_definition: str | None = Field(
        default=None,
        description=(
            "The definition of the schema describing the concept set,"
            " in case of type CONTEXT_FREE_GRAMMAR_XXX"
        ),
    )
    schema_uri: str | None = Field(
        default=None,
        description=(
            "The URI to the schema describing the concept set,"
            " in case of type CONTEXT_FREE_GRAMMAR_XXX"
        ),
    )
    description: str | None = Field(
        default=None, description="The description of the concept set."
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.type == enum.ConceptSetType.REGULAR_LANGUAGE:
            if not self.regex:
                raise AssertionError(f"Type {self.type.value} requires regex")
        elif self.type in {
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_JSON,
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_XML,
        }:
            if not self.schema_definition and not self.schema_uri:
                raise AssertionError(
                    f"Type {self.type.value} requires schema_definition or schema_uri"
                )
        if self.schema_definition and self.schema_uri:
            raise AssertionError(
                "Only one of schema_definition or schema_uri can be set"
            )
        return self


class ConceptSetMember(Model):
    """
    The membership of a concept in a concept set.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="concept_set_members",
        table_name="concept_set_member",
        persistable=True,
        keys=create_keys({1: ("concept_set_id", "concept_id")}),
        links=create_links(
            {
                1: ("concept_set_id", ConceptSet, "concept_set"),
                2: ("concept_id", Concept, "concept"),
            }
        ),
    )
    concept_set_id: UUID = Field(description="The ID of the concept set. FOREIGN KEY")
    concept_set: ConceptSet | None = Field(default=None, description="The concept set")
    concept_id: UUID = Field(description="The ID of the concept. FOREIGN KEY")
    concept: Concept | None = Field(None, description="The concept")
    rank: int | None = Field(
        None,
        description=(
            "The rank of the concept within the set,"
            " in case of an ORDINAL or INTERVAL concept set"
        ),
    )


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
