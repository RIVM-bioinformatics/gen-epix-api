import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import DataCollection, IdentifierIssuer
from gen_epix.fastapp.domain import Entity, create_keys
from gen_epix.fastapp.domain.util import create_links
from gen_epix.seqdb.domain.model.seq.base import CodeMixin


class Sample(Model, CodeMixin):
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
        keys=create_keys({1: "code"}),
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
    )
    sample_id: str = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    data_collection_id: str = Field(
        description="The unique identifier for the data collection. FOREIGN KEY"
    )


class SampleIdentifier(Model):
    """
    An external identifier for a sample, issued by some identifier issuer. A sample
    can have multiple external identifiers, but only one per identifier issuer.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="sample_identifiers",
        table_name="sample_identifier",
        persistable=True,
        keys=create_keys({1: ("identifier", "identifier_issuer_id")}),
        links=create_links(
            {1: ("identifier_issuer_id", IdentifierIssuer, "identifier_issuer")}
        ),
    )
    sample_id: str = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    identifier_issuer_id: UUID = Field(
        description="The ID of the identifier issuer. FOREIGN KEY"
    )
    identifier: str = Field(
        description="The external identifier for the sample, with whitespace stripped from both ends.",
        max_length=255,
    )
    identifier_issuer: IdentifierIssuer = Field(
        description="The identifier issuer.",
    )

    @field_validator("identifier", mode="before")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        return v.strip()
