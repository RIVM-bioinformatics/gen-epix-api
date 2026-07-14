import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier, DataCollection
from gen_epix.fastapp.domain import Entity, create_keys
from gen_epix.fastapp.domain.util import create_links


class Sample(Model):
    """
    The original physical sample (specimen) on which all measurements were performed
    either directly or through some derived samples. Derived samples such as cultures
    or library preps for sequencing are not modelled.

    Descriptive properties of the sample, such as the sampling date, are not
    modelled explicitly but can be stored in the props attribute as key-value pairs.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="samples",
        table_name="sample",
        persistable=True,
        links=create_links(
            {
                1: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
            }
        ),
    )
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the sample was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the sample was created"
    )
    code: str | None = Field(
        default=None,
        max_length=255,
        description="A code for the sample for further reference",
    )
    props: dict[str, str | int | float | None] = Field(
        default_factory=dict, description="The properties of the sample."
    )

    @model_validator(mode="before")
    def _validate_model(cls, values: dict) -> dict:
        # Strip code of whitespace
        code = values.get("code")
        if code is not None:
            values["code"] = code.strip()
        # Ensure props is a dict
        props = values.get("props")
        if isinstance(props, str):
            values["props"] = json.loads(props)
        elif props is None:
            values["props"] = {}
        return values


class HasSampleMixin:
    sample_id: UUID = Field(
        description="The unique identifier for the sample from which these results were obtained. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")


class SampleDataCollectionLink(Model):
    """
    Association between a sample and a data collection. A sample can thus be part
    of multiple data collections.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="sample_data_collection_links",
        table_name="sample_data_collection_link",
        persistable=True,
        keys=create_keys({1: ("sample_id", "data_collection_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: (
                    "data_collection_id",
                    DataCollection,
                    "data_collection",
                ),
            }
        ),
    )
    sample_id: UUID = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    data_collection_id: UUID = Field(
        description="The unique identifier for the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection."
    )


class SampleIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        Sample,
        snake_case_plural_name="sample_identifiers",
        table_name="sample_identifier",
    )
    NAME: ClassVar = "SampleIdentifier"
    MODEL_CLASS: ClassVar = Sample
