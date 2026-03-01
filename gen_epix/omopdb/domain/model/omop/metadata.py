"""
Metadata domain - OMOP CDM v6.0 metadata tables.

This module contains classes that store metadata about the CDM instance itself,
including source information and general metadata about the dataset.

Classes:
- CdmSource: Information about the CDM source data
- Metadata: Additional metadata key-value pairs
"""

from datetime import date, datetime
from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field, field_validator

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.base import validate_int_for_uuid_field
from gen_epix.omopdb.domain.model.omop.ontology import Concept


class CdmSource(Model):
    """The CDM_SOURCE table contains detail about the source database and the process used to transform the data into the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="CdmSources",
        table_name="cdm_source",
        persistable=True,
        id_field_name="cdm_source_id",
    )
    cdm_source_name: str = Field(
        description="User guidance:\nThe name of the CDM instance.\nETL conventions:\nNone",
        max_length=255,
    )
    cdm_source_abbreviation: str = Field(
        description="User guidance:\nThe abbreviation of the CDM instance.\nETL conventions:\nNone",
        max_length=25,
    )
    cdm_holder: str = Field(
        description="User guidance:\nThe holder of the CDM instance.\nETL conventions:\nNone",
        max_length=255,
    )
    source_description: str | None = Field(
        default=None,
        description="User guidance:\nThe description of the CDM instance.\nETL conventions:\nNone",
    )
    source_documentation_reference: str | None = Field(
        default=None,
        description="User guidance:\nRefers to a publication or web resource describing the source data\nETL conventions:\n e.g. a data dictionary.",
        max_length=255,
    )
    cdm_etl_reference: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nVersion of the ETL script used. e.g. link to the Git release",
        max_length=255,
    )
    source_release_date: date = Field(
        description="User guidance:\nThe date the data was extracted from the source system. In some systems that is the same as the date the ETL was run. Typically the latest even date in the source is on the source_release_date.\nETL conventions:\nNone"
    )
    cdm_release_date: date = Field(
        description="User guidance:\nThe date the ETL script was completed. Typically this is after the source_release_date.\nETL conventions:\nNone"
    )
    cdm_version: str | None = Field(
        default=None,
        description="User guidance:\nVersion of the OMOP CDM used as string. e.g. v5.4\nETL conventions:\nNone",
        max_length=10,
    )
    cdm_version_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the version of the CDM.\nETL conventions:\nYou can find all concepts that represent the CDM versions using the query: `SELECT * FROM CONCEPT WHERE   VOCABULARY_ID = 'CDM' AND CONCEPT_CLASS = 'CDM'`"
    )
    vocabulary_version: str = Field(
        description="User guidance:\nVersion of the OMOP standardised vocabularies loaded\nETL conventions:\nYou can find the version of your Vocabulary using the query: `SELECT vocabulary_version from vocabulary  where vocabulary_id = 'None'`",
        max_length=20,
    )
    cdm_source_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone",
    )

    @field_validator("cdm_version_concept_id", mode="before")
    @classmethod
    def _validate_int_for_uuid(cls, value: Any | None) -> UUID | None:
        return validate_int_for_uuid_field(value)


class Metadata(Model):
    """The METADATA table contains metadata information about a dataset that has been transformed to the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Metadatas",
        table_name="metadata",
        persistable=True,
        id_field_name="metadata_id",
        links=create_links(
            {
                1: ("metadata_concept_id", Concept, None),
                2: ("metadata_type_concept_id", Concept, None),
                3: ("value_as_concept_id", Concept, None),
            }
        ),
    )
    metadata_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe unique key given to a Metadata record.\nETL conventions:\nAttribute value is auto-generated",
    )
    metadata_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_type_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    name: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=250
    )
    value_as_string: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=250,
    )
    value_as_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    value_as_number: float | None = Field(
        default=None,
        description="User guidance:\nThis is the numerical value of the result of the Metadata, if applicable and available. It is not expected that all Metadata will have numeric results, rather, this field is here to house values should they exist.\nETL conventions:\nNone",
    )
    metadata_date: date | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_datetime: datetime | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )

    @field_validator(
        "metadata_concept_id",
        "metadata_type_concept_id",
        "value_as_concept_id",
        mode="before",
    )
    @classmethod
    def _validate_int_for_uuid(cls, value: Any | None) -> UUID | None:
        return validate_int_for_uuid_field(value)
