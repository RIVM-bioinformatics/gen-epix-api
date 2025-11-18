import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum


class Taxon(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxa",
        table_name="taxon",
        persistable=True,
        keys=create_keys({1: "code"}),
    )
    code: str = Field(description="The code of the taxon", max_length=255)
    name: str = Field(description="The name of the taxon", max_length=255)
    rank: enum.TaxonRank = Field(description="The rank of the taxon")
    ncbi_taxid: int | None = Field(
        default=None, description="The NCBI Taxonomy ID of the taxon"
    )
    ictv_ictv_id: str | None = Field(
        default=None, description="The ICTV ID of the taxon", max_length=255
    )
    snomed_sctid: int | None = Field(
        default=None, description="The Snomed CT ID of the taxon"
    )
    ncbi_ancestor_taxids: list[int] | None = Field(
        default=None,
        description="The NCBI taxon IDs of the ancestors, sorted from highest to lowest rank",
    )
    ancestor_taxon_ids: list[UUID] = Field(
        description="The IDs of the ancestor taxa, sorted from highest to lowest rank"
    )

    @field_validator("ncbi_ancestor_taxids", mode="before")
    @classmethod
    def _validate_ncbi_ancestor_taxids(cls, value: list[int] | str) -> list[int]:
        if isinstance(value, str):
            return [int(x) for x in json.loads(value)]
        return value

    @field_validator("ancestor_taxon_ids", mode="before")
    @classmethod
    def _validate_ancestor_taxon_ids(cls, value: list[UUID] | str) -> list[UUID]:
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_serializer("ancestor_taxon_ids", mode="plain")
    def _serialize_ancestor_taxon_ids(self, value: list[UUID]) -> list[str]:
        return [str(x) for x in value]


class TaxonSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_sets",
        table_name="taxon_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the taxon set", max_length=255)
    name: str = Field(description="The name of the taxon set", max_length=255)


class TaxonSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_set_members",
        table_name="taxon_set_member",
        persistable=True,
        keys=create_keys({1: "taxon_set_id", 2: "taxon_id"}),
        links=create_links(
            {
                1: ("taxon_set_id", TaxonSet, "taxon_set"),
                2: ("taxon_id", Taxon, "taxon"),
            }
        ),
    )
    taxon_set_id: UUID = Field(description="The ID of the taxon set. FOREIGN KEY")
    taxon_set: TaxonSet = Field(description="The taxon set")
    taxon_id: UUID = Field(description="The ID of the taxon. FOREIGN KEY")
    taxon: Taxon = Field(description="The taxon")
