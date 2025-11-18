from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import DataCollection, IdentifierIssuer
from gen_epix.fastapp.domain import Entity, create_keys
from gen_epix.fastapp.domain.util import create_links
from gen_epix.seqdb.domain.model.seq.base import CodeMixin


class Sample(Model, CodeMixin):
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
        description="The ID of the data collection where the case was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case was created"
    )
    props: dict[str, str] = Field(
        default_factory=dict, description="The properties of the sample."
    )


class SampleDataCollectionLink(Model):
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
