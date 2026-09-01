"""Define seqdb domain models for domain.model.seq.sample."""

import json
from typing import Annotated, ClassVar
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier, DataCollection
from gen_epix.fastapp.domain import Entity, create_keys
from gen_epix.fastapp.domain.util import create_links


class Sample(Model):
    """Represent the original specimen from which seqdb data was derived.

    Derived cultures and library preparations are not modelled. Additional sample
    properties, such as collection date, are stored as key-value pairs.

    Model validation: Codes are stripped of surrounding whitespace. Properties may
    be supplied as JSON and are normalized to a dictionary.
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
        """Normalize the sample code and JSON-encoded properties."""
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
    """Provide sample relationship fields to models derived from a sample."""

    # Annotation-only: an assigned Field lingers as class attr -> pydantic shadow warning
    sample_id: Annotated[
        UUID,
        Field(
            description="The unique identifier for the sample from which these results were obtained. FOREIGN KEY"
        ),
    ]
    sample: Annotated[Sample | None, Field(default=None, description="The sample.")]


class SampleDataCollectionLink(Model):
    """Associate a sample with one of the data collections it belongs to."""

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
    """Associate an external identifier with a sample."""

    ENTITY: ClassVar = BaseIdentifier.create_entity(
        Sample,
        snake_case_plural_name="sample_identifiers",
        table_name="sample_identifier",
    )
    NAME: ClassVar = "SampleIdentifier"
    MODEL_CLASS: ClassVar = Sample
