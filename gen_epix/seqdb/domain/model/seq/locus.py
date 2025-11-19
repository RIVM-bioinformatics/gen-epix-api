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


class LocusCode(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_codes",
        table_name="locus_code",
        persistable=True,
        keys=create_keys({1: ("naming_scheme")}),
    )
    naming_scheme: str = Field(
        description="The naming scheme used for the locus codes.",
        max_length=255,
    )
    code_map: dict[str, UUID] = Field(
        description="Mapping from locus codes to locus IDs. Each code may have a max length of 255 characters.",
    )

    @field_validator("code_map", mode="before")
    @classmethod
    def _validate_code_map(cls, value: dict[str, UUID] | str) -> dict[str, UUID]:
        """
        Validate and convert code_map representation to a dict[str, UUID]. When given as a
        string, it is assumed to be a JSON object.
        """
        dict_value: dict = value  # type: ignore[assignment]
        if isinstance(value, str):
            dict_value = json.loads(value)
        if len(set(dict_value.values())) != len(dict_value):
            raise ValueError("All locus IDs in code_map must be unique.")
        if any(len(x) > 255 for x in dict_value.keys()):
            raise ValueError("All locus codes in code_map must have max length of 255.")
        return dict_value


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


class Allele(Model, SeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alleles",
        table_name="allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "seq_hash")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")


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
