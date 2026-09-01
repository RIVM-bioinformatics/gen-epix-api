"""Define seqdb domain models for domain.model.seq.locus."""

import json
from functools import cached_property
from typing import ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.fastapp.domain.util import create_multi_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import BaseSeq


class Locus(Model):
    """A genetic locus, e.g. a gene or other genomic region of interest. The locus can be
    defined on any taxonomic level, e.g. species, lineage, etc. As such, depending on
    the analysis, two loci may actually represent the same genomic region, but defined
    for lower taxonomic levels than the one used in the analysis. This information,
    where relevant, can be captured in a LocusSet or can reside entirely outside the
    application.

    A locus is immutable: once created, it cannot be deleted. Its properties
    should not change semantically either. As such, locus IDs can safely be
    referenced in other models and outside of the application.

    Model validation: Empty gene-product codes are normalized to ``None`` and a
    non-empty gene-product code is permitted only for gene loci.

    Model serialization: Locus types are emitted by their string enum value.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="loci",
        table_name="locus",
        persistable=True,
        keys=create_keys({1: "code"}),
    )
    code: str = Field(
        description="A standard code for the locus. UNIQUE", max_length=255
    )
    name: str | None = Field(
        default=None, description="The name of the locus.", max_length=255
    )
    description: str | None = Field(
        default=None, description="A description of the locus."
    )
    locus_type: enum.LocusType = Field(
        default=enum.LocusType.UNKNOWN, description="The type of the locus."
    )
    gene_product_code: str | None = Field(
        default=None,
        description="A code for the gene product, only in case the locus is a gene and if available. An empty string is treated as None.",
        max_length=255,
    )

    @field_validator("gene_product_code", mode="before")
    @classmethod
    def _validate_gene_product_code(cls, value: str | None) -> str | None:
        """Normalize an empty gene-product code to ``None``."""
        if isinstance(value, str) and len(value) == 0:
            return None
        return value

    @model_validator(mode="after")
    def _validate_locus(self) -> Self:
        """Restrict gene-product codes to loci typed as genes."""
        if self.locus_type != enum.LocusType.GENE and self.gene_product_code:
            raise ValueError("gene_product_code must be provided for locus_type GENE.")
        return self

    @field_serializer("locus_type", mode="plain")
    def _serialize_locus_type(self, value: str | enum.LocusType) -> str:
        """Serialize a locus-type enum as its string value."""
        if isinstance(value, enum.LocusType):
            return value.value
        return value


class LocusSet(Model):
    """Define an immutable ordered locus set for locus-based analyses."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_sets",
        table_name="locus_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        multi_links=create_multi_links([("locus_ids", Locus)]),
    )
    code: str = Field(description="The code of the locus set.", max_length=255)
    name: str = Field(description="The name of the locus set.", max_length=255)
    locus_ids: list[UUID] = Field(
        description="The ordered IDs of the loci in the locus set."
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="The number of loci in the locus set."
    )
    @cached_property
    def n_loci(self) -> int:
        """Return the number of loci in this set."""
        return len(self.locus_ids)

    @field_validator("locus_ids", mode="before")
    @classmethod
    def _validate_locus_ids(cls, value: list[UUID] | str) -> list[UUID]:
        """Normalize a JSON locus-ID list to UUID objects."""
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_serializer("locus_ids", mode="plain")
    def _serialize_locus_ids(self, value: list[UUID]) -> list[str]:
        """Serialize ordered locus identifiers as strings."""
        return [str(x) for x in value]


class LocusCodeMap(Model):
    """Map external locus codes to seqdb locus identifiers."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_code_maps",
        table_name="locus_code_map",
        persistable=True,
        keys=create_keys({1: ("code")}),
        multi_links=create_multi_links([("code_map", Locus)]),
    )
    code: str = Field(
        description="The naming scheme used for the locus codes.",
        max_length=255,
    )
    code_map: dict[str, UUID] = Field(
        description="Mapping from locus codes to locus IDs. Each code may have a max length of 255 characters.",
    )

    @field_validator("code_map", mode="before")
    @classmethod
    def _validate_code_map(cls, value: dict[str, UUID] | str) -> dict[str, UUID]:
        """Normalize a JSON locus-code map and enforce its key length limit."""
        dict_value: dict = value  # type: ignore[assignment]
        if isinstance(value, str):
            dict_value = json.loads(value)
        if any(len(x) > 255 for x in dict_value.keys()):
            raise ValueError("All locus codes in code_map must have max length of 255.")
        return dict_value

    @field_serializer("code_map", mode="plain")
    def _serialize_locus_ids(self, value: dict[str, UUID]) -> dict[str, str]:
        """Serialize locus-code-map identifier values as strings."""
        return {x: str(y) for x, y in value.items()}


class RefAllele(BaseSeq):
    """Represent an immutable sequence-hashed reference allele for a locus."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_alleles",
        table_name="ref_allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "index")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    NAME: ClassVar = "RefAllele"

    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
    index: int = Field(
        description="The index (ordinal number) of the reference allele for the locus."
    )


class Allele(BaseSeq):
    """Represent an immutable sequence-hashed allele first observed at a locus."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alleles",
        table_name="allele",
        persistable=True,
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    NAME: ClassVar = "Allele"

    locus_id: UUID = Field(
        description="The unique identifier for the locus that the allele was first observed for. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
