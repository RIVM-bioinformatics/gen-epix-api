# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.reference_data import (
    CaseSetCategory,
    CaseSetStatus,
    CaseType,
)
from gen_epix.casedb.domain.model.subject import Subject
from gen_epix.commondb.domain.model import DataCollection, Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class Case(Model):
    """
    A class representing a case.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cases",
        table_name="case",
        persistable=True,
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: ("subject_id", Subject, "subject"),
                3: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
            }
        ),
    )
    code: str | None = Field(
        default=None, description="A code for the case for further reference."
    )
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")
    subject_id: UUID | None = Field(
        default=None, description="The ID of the subject. FOREIGN KEY"
    )
    subject: Subject | None = Field(default=None, description="The subject")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case was created"
    )
    count: int | None = Field(
        default=None,
        description="The number of cases that this case represents, if not one. This can be used to store aggregated cases (n>=0) as well as reference data (n=0).",
        gt=0,
    )
    case_date: datetime = Field(
        default_factory=datetime.now,
        description="The datetime of the case used for sorting results, limiting results and statistics such as first and last case date. Normally re-calculated from the case content variables upon persisting. Default is the current datetime.",
    )
    content: dict[UUID, str] = Field(
        description=r"The data content of the case as {case_type_col_id: str_value}. Only case type columns defined for the case type of the case should be present here, and if no value is present, the key should be omitted."
    )

    @field_serializer("content", mode="plain")
    def _serialize_content(self, value: dict[UUID, str]) -> dict[str, str]:
        return {str(x): y for x, y in value.items()}


class CaseDataCollectionLink(Model):
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
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_sets",
        table_name="case_set",
        persistable=True,
        keys=create_keys({1: "name"}),
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
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case set was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case set was created"
    )
    name: str = Field(description="The name of a case set, UNIQUE", max_length=255)
    description: str = Field(
        description="The description of a case set", max_length=10000
    )
    created_at: datetime = Field(
        description="The datetime of the case set creation",
        default_factory=datetime.now,
    )
    case_set_category_id: UUID = Field(
        description="The id of the category of the case set"
    )
    case_set_category: CaseSetCategory | None = Field(
        default=None, description="The category of the case set"
    )
    case_set_status_id: UUID = Field(description="The id of the status of the case set")
    case_set_status: CaseSetStatus | None = Field(
        default=None, description="The status of the case set"
    )


class CaseSetMember(Model):
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
