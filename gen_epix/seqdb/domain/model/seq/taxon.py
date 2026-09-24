"""Define seqdb domain models for domain.model.seq.taxon."""

import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum


class Taxon(Model):
    """Represents a taxonomic unit in a unified taxonomy.

    A single unified taxonomy is modelled rather than separate taxonomies such as NCBI
    Taxonomy
    and ICTV taxonomy. The corresponding taxon codes for these taxonomies, as
    well as SNOMED-CT organism codes, can be added. The responsibility for creating
    a single unified taxonomy lies outside of the application.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxa",
        table_name="taxon",
        persistable=True,
        keys=create_keys({1: "code"}),
    )

    NCBI_TAXON_PREFIX: ClassVar[str] = "NCBI:txid"

    code: str = Field(description="The code of the taxon", max_length=255)
    name: str = Field(description="The name of the taxon", max_length=255)
    rank: enum.TaxonRank = Field(description="The rank of the taxon")
    ncbi_taxid: int | None = Field(
        default=None,
        description="The NCBI Taxonomy ID of the taxon, as an int excluding the NCBI:txid prefix",
    )
    ictv_ictv_id: str | None = Field(
        default=None, description="The ICTV ID of the taxon", max_length=255
    )
    snomed_sctid: int | None = Field(
        default=None, description="The Snomed CT ID of the taxon"
    )
    ncbi_ancestor_taxids: list[int] | None = Field(
        default=None,
        description="The NCBI taxon IDs, excluding the NCBI:txid prefix, of the ancestors, sorted from highest to lowest rank",
    )
    ancestor_taxon_ids: list[UUID] = Field(
        description="The IDs of the ancestor taxa, sorted from highest to lowest rank"
    )

    @field_validator("ncbi_taxid", mode="before")
    @classmethod
    def _validate_ncbi_taxid(cls, value: int | float | str) -> int:
        """Normalize an NCBI taxon identifier, accepting its standard prefix."""
        if isinstance(value, str):
            return int(value.replace(cls.NCBI_TAXON_PREFIX, ""))
        return int(value)

    @field_validator("ncbi_ancestor_taxids", mode="before")
    @classmethod
    def _validate_ncbi_ancestor_taxids(cls, value: list[int] | str) -> list[int]:
        """Normalize JSON or prefixed NCBI ancestor identifiers to integers."""
        if isinstance(value, str):
            return [
                (
                    int(x)
                    if isinstance(x, (int, float))
                    else int(x.replace(cls.NCBI_TAXON_PREFIX, ""))
                )
                for x in json.loads(value)
            ]
        return value

    @field_validator("ancestor_taxon_ids", mode="before")
    @classmethod
    def _validate_ancestor_taxon_ids(cls, value: list[UUID] | str) -> list[UUID]:
        """Normalize a JSON ancestor identifier list to UUID objects."""
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_validator("rank", mode="before")
    @classmethod
    def _validate_rank(cls, value: str | enum.TaxonRank) -> enum.TaxonRank:
        """Normalize a taxon rank, accepting spaced NCBI rank names."""
        if isinstance(value, str):
            value = value.upper().replace(" ", "_")
            return enum.TaxonRank(value)
        return value

    @field_serializer("ancestor_taxon_ids", mode="plain")
    def _serialize_ancestor_taxon_ids(self, value: list[UUID]) -> list[str]:
        """Serialize ancestor taxon identifiers as strings."""
        return [str(x) for x in value]


class TaxonSet(Model):
    """Represents a set of taxa, for example a set of taxa that are relevant for a specific
    analysis or application.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_sets",
        table_name="taxon_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the taxon set", max_length=255)
    name: str = Field(description="The name of the taxon set", max_length=255)


class TaxonSetMember(Model):
    """Represents a member of a taxon set, representing the inclusion of a specific taxon
    in a taxon set.
    """

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
