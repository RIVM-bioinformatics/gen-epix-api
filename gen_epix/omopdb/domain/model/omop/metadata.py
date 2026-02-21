"""
Metadata domain - OMOP CDM v6.0 metadata tables.

This module contains classes that store metadata about the CDM instance itself,
including source information and general metadata about the dataset.

Classes:
- CdmSource: Information about the CDM source data
- Metadata: Additional metadata key-value pairs
"""

from datetime import date, datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
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
    cdm_source_abbreviation: str | None = Field(
        default=None,
        description="User guidance:\nThe abbreviation of the CDM instance.\nETL conventions:\nNone",
        max_length=25,
    )
    cdm_holder: str | None = Field(
        default=None,
        description="User guidance:\nThe holder of the CDM instance.\nETL conventions:\nNone",
        max_length=255,
    )
    source_description: str | None = Field(
        default=None,
        description="User guidance:\nThe description of the CDM instance.\nETL conventions:\nNone",
    )
    source_documentation_reference: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=255,
    )
    cdm_etl_reference: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nPut the link to the CDM version used.",
        max_length=255,
    )
    source_release_date: date | None = Field(
        default=None,
        description="User guidance:\nThe release date of the source data.\nETL conventions:\nNone",
    )
    cdm_release_date: date | None = Field(
        default=None,
        description="User guidance:\nThe release data of the CDM instance.\nETL conventions:\nNone",
    )
    cdm_version: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=10,
    )
    vocabulary_version: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=20,
    )
    cdm_source_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


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
    metadata_date: date | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_datetime: datetime | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )
