# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later
"""Define persistable operational models for cases and case sets.

The module provides cases, identifiers, case sets, memberships, and their links
to data collections for use by the case domain and persistence layer.
"""

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.ref_data import (
    CaseSetCategory,
    CaseSetStatus,
    CaseType,
    Col,
)
from gen_epix.casedb.domain.model.geo import Region
from gen_epix.casedb.domain.model.ontology import Concept
from gen_epix.commondb.domain.model import DataCollection, Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.fastapp.domain.util import create_multi_links


class Case(Model):
    """Represents an epidemiological case and its typed content."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cases",
        table_name="case",
        persistable=True,
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
            }
        ),
        multi_links=create_multi_links(
            [
                ("content", Col),  # content dict keys
                ("content", Region),  # some content dict values
                ("content", Concept),  # some content dict values
            ]
        ),
    )
    code: str | None = Field(
        default=None, description="A code for the case for further reference."
    )
    case_type_id: UUID = Field(description="The ID of the CaseType. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The CaseType")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case was created"
    )
    cohort: dict[UUID, UUID | None] = Field(
        default_factory=dict,
        description=r"The cohort(s) that this case belongs to, as {cohort_id: cohort_definition_id}. This is used for traceability of the case to any omopdb cohorts (typically one) that it was derived from. None values are retained as null, and UUID keys and values are serialized as strings.",
    )
    count: int = Field(
        default=1,
        description="The number of cases that this case represents, if not one. This can be used to store aggregated cases (n>1) as well as reference data (n=0).",
        ge=0,
    )
    case_date: datetime = Field(
        default_factory=datetime.now,
        description="The datetime of the case used for sorting results, limiting results and statistics such as first and last case date. Normally re-calculated from the case content variables upon persisting. Default is the current datetime.",
    )
    content: dict[UUID, str | None] = Field(
        description=r"The data content of the case as {col_id: str_value | None}. Only columns defined for the CaseType of the case should be present here, and if no value is present, the key should be omitted. None content values are allowed to support deletion of keys."
    )

    @field_serializer("cohort", mode="plain")
    def _serialize_cohort(
        self, value: dict[UUID, UUID | None]
    ) -> dict[str, str | None]:
        """Serialize cohort UUID keys and non-null values as strings."""
        return {str(x): None if y is None else str(y) for x, y in value.items()}

    @field_serializer("content", mode="plain")
    def _serialize_content(
        self, value: dict[UUID, str | None]
    ) -> dict[str, str | None]:
        """Serialize content UUID keys as strings while retaining values."""
        return {str(x): None if y is None else y for x, y in value.items()}


class CaseIdentifier(BaseIdentifier):
    """Represents an external identifier associated with a case."""

    ENTITY: ClassVar = BaseIdentifier.create_entity(
        Case,
        relationship_field_name="case",
        snake_case_plural_name="case_identifiers",
        table_name="case_identifier",
    )
    NAME: ClassVar = "CaseIdentifier"
    MODEL_CLASS: ClassVar = Case

    case: Case | None = Field(
        default=None, description="The case associated with this identifier."
    )


class CaseDataCollectionLink(Model):
    """Represents a case membership link to a data collection."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_data_collection_links",
        table_name="case_data_collection_link",
        persistable=True,
        keys=create_keys({1: ("case_id", "data_collection_id")}),
        links=create_links(
            {
                1: ("case_id", Case, "case"),
                2: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
    )
    case_id: UUID = Field(description="The ID of the case. FOREIGN KEY")
    case: Case | None = Field(default=None, description="The case")
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )


class CaseSet(Model):
    """Represents a named, typed collection of epidemiological cases."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_sets",
        table_name="case_set",
        persistable=True,
        keys=create_keys({1: "name", 2: "code"}),
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
                3: ("case_set_category_id", CaseSetCategory, "case_set_category"),
                4: ("case_set_status_id", CaseSetStatus, "case_set_status"),
            }
        ),
    )
    case_type_id: UUID = Field(description="The ID of the CaseType. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The CaseType")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case set was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case set was created"
    )
    name: str = Field(description="The name of a case set, UNIQUE", max_length=255)
    code: str = Field(description="The code of a case set, UNIQUE", max_length=255)
    description: str = Field(description="The description of a case set")
    case_set_date: datetime = Field(
        description="The datetime of the case set creation",
        default_factory=datetime.now,
    )
    case_set_category_id: UUID = Field(
        description="The CaseSetCategory ID. FOREIGN KEY"
    )
    case_set_category: CaseSetCategory | None = Field(
        default=None, description="The category of the case set"
    )
    case_set_status_id: UUID = Field(description="The CaseSetStatus ID. FOREIGN KEY")
    case_set_status: CaseSetStatus | None = Field(
        default=None, description="The status of the case set"
    )


class CaseSetMember(Model):
    """Represents a case's membership of a case set."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_members",
        table_name="case_set_member",
        persistable=True,
        keys=create_keys({1: ("case_set_id", "case_id")}),
        links=create_links(
            {1: ("case_set_id", CaseSet, "case_set"), 2: ("case_id", Case, "case")}
        ),
    )
    case_set_id: UUID = Field(description="The ID of the case set. FOREIGN KEY")
    case_set: CaseSet | None = Field(default=None, description="The case set")
    case_id: UUID = Field(description="The ID of the case. FOREIGN KEY")
    case: Case | None = Field(default=None, description="The case")
    classification: enum.CaseClassification | None = Field(
        default=None, description="The classification of the case"
    )


class CaseSetDataCollectionLink(Model):
    """Represents a case set membership link to a data collection."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_data_collection_links",
        table_name="case_set_data_collection_link",
        persistable=True,
        keys=create_keys({1: ("case_set_id", "data_collection_id")}),
        links=create_links(
            {
                1: ("case_set_id", CaseSet, "case_set"),
                2: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
    )
    case_set_id: UUID = Field(description="The ID of the case set. FOREIGN KEY")
    case_set: CaseSet | None = Field(default=None, description="The case set")
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )
