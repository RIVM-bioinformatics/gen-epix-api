import json
from functools import cached_property
from typing import ClassVar, Self
from uuid import UUID

from pydantic import (Field, computed_field, field_serializer, field_validator,
                      model_validator)

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import BaseSeq


class Locus(Model):
    """
    A genetic locus, e.g. a gene or other genomic region of interest.

    A locus is immutable: once created, it cannot be deleted. Its properties
    should not change semantically either. As such, locus IDs can safely be
    referenced in other models and outside of the application.
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
        if isinstance(value, str) and len(value) == 0:
            return None
        return value

    @model_validator(mode="after")
    def _validate_locus(self) -> Self:
        if self.locus_type != enum.LocusType.GENE and self.gene_product_code:
            raise ValueError("gene_product_code must be provided for locus_type GENE.")
        return self

    @field_serializer("locus_type", mode="plain")
    def _serialize_locus_type(self, value: str | enum.LocusType) -> str:
        if isinstance(value, enum.LocusType):
            return value.value
        return value


class LocusSet(Model):
    """
    An ordered set of loci. This can be used to define e.g. schemes for wgMLST typing
    or other locus-based analyses. Because the set is ordered, i.e. a list of unique
    locus IDS, it can also be used to define the order of loci in allele profiles and
    other analyses.

    A locus set is immutable: once created, it cannot be deleted or updated. As such,
    locus set IDs and names can safely be referenced in other models and outside of the
    application.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_sets",
        table_name="locus_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
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
        """"""
        return len(self.locus_ids)

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


class LocusCodeMap(Model):
    """
    A mapping from locus codes to locus IDs for a specific naming scheme.
    This can be used e.g. to translate locus codes used by a particular
    application to the IDs used in this application, thereby facilitating
    interoperability.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_code_maps",
        table_name="locus_code_map",
        persistable=True,
        keys=create_keys({1: ("code")}),
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
        """
        Validate and convert code_map representation to a dict[str, UUID]. When given as a
        string, it is assumed to be a JSON object.
        """
        dict_value: dict = value  # type: ignore[assignment]
        if isinstance(value, str):
            dict_value = json.loads(value)
        if any(len(x) > 255 for x in dict_value.keys()):
            raise ValueError("All locus codes in code_map must have max length of 255.")
        return dict_value

    @field_serializer("code_map", mode="plain")
    def _serialize_locus_ids(self, value: dict[str, UUID]) -> dict[str, str]:
        return {x: str(y) for x, y in value.items()}


class RefAllele(BaseSeq):
    """
    A reference allele for a locus. This can be an actual sequence or an
    artificial construct, typically then a consensus sequence. It can be used
    e.g. as a reference for alignment of other alleles for the locus or for
    reducing storage requirements of alleles.

    A reference allele is immutable: once created, it cannot be deleted or updated. As
    such, reference allele IDs can safely be referenced in other models and outside of
    the application.

    The ID of the reference allele is equal to the hash of the sequence. As such, the
    ID of the reference allele can be computed outside of the application as well.
    """

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
    """
    An allele for a locus, i.e., a specific DNA sequence variant observed at that locus.
    Any IUPAC ambiguity codes are allowed in the sequence.

    An allele is immutable: once created, it cannot be deleted or updated. As such,
    allele IDs can safely be referenced in other models and outside of the application.

    The ID of the allele is equal to the hash of the sequence. As such, the ID of the
    allele can be computed outside of the application as well, e.g., to improve
    performance. In case of a collision, i.e., two different sequences yielding the same
    hash, the newer allele cannot be persisted. The probability of such collisions is
    extremely low: about 10^15 alleles would need to be stored for a one-in-a-billion
    chance of a collision. If such a collision does occur, you could send it to your
    nearest cryptographer, as they will be thrilled to investigate it. A word of
    caution though: this will lead to the discovery that SHA256 is cryptographically
    broken, which in turn will lead to the discovery that P=NP. This will lead to the
    collapse of modern cryptography, triggering a period of global chaos that will
    eventually lead to nuclear armageddon and bring about the end of human civilization
    as we know it. No liability is accepted for this chain of events.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alleles",
        table_name="allele",
        persistable=True,
        links=create_links({1: ("locus_id", Locus, "locus")}),
    )
    NAME: ClassVar = "Allele"

    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
