import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain.model.seq.base import QualityMixin, SeqMixin
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class Locus(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="loci",
        table_name="locus",
        persistable=True,
        keys=create_keys({1: "code"}),
    )
    code: str = Field(description="The code of the locus.", max_length=255)
    gene_code: str | None = Field(
        default=None,
        description="The code of the gene, if the locus corresponds to one and a code is available.",
        max_length=255,
    )
    product_name: str | None = Field(
        default=None,
        description="The name of the gene product, if available.",
        max_length=255,
    )


class Allele(Model, SeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alleles",
        table_name="allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "seq_hash_sha256")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")


class LocusSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_sets",
        table_name="locus_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the locus set.", max_length=255)
    name: str = Field(description="The name of the locus set.", max_length=255)
    n_loci: int = Field(description="The number of loci in the locus set.")
    locus_ids: list[UUID] = Field(
        description="The ordered IDs of the loci in the locus set."
    )

    @field_validator("locus_ids", mode="before")
    @classmethod
    def _validate_locus_ids(cls, value: list[UUID] | str) -> list[UUID]:
        """
        Validate and convert locus_ids representation to a list[UUID]. When given as a
        string, it is assumed to be a JSON list of UUID string representations.
        """
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_serializer("locus_ids", mode="plain")
    def _serialize_locus_ids(self, value: list[UUID]) -> list[str]:
        return [str(x) for x in value]


class LocusSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_set_members",
        table_name="locus_set_member",
        persistable=True,
        keys=create_keys({1: ("locus_set_id", "locus_id")}),
        links=create_links(
            {
                1: ("locus_set_id", LocusSet, "locus_set"),
                2: ("locus_id", Locus, "locus"),
            }
        ),
    )
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
    index: int = Field(
        description="The index (ordinal number) of the locus in the locus set."
    )


class RefAllele(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_alleles",
        table_name="ref_allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "index")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
    index: int = Field(
        description="The index (ordinal number) of the reference allele for the locus."
    )


class TaxonLocusLink(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_locus_links",
        table_name="taxon_locus_link",
        persistable=True,
        keys=create_keys({1: ("taxon_id", "locus_id")}),
        links=create_links(
            {1: ("taxon_id", Taxon, "taxon"), 2: ("locus_id", Locus, "locus")}
        ),
    )
    taxon_id: UUID = Field(
        description="The unique identifier for the taxon. FOREIGN KEY"
    )
    taxon: Taxon | None = Field(default=None, description="The taxon.")
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
