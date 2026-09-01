"""Define seqdb domain models for domain.model.seq.ref_seq."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain.model.seq.base import BaseSeq
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class RefSeq(BaseSeq):
    """
    Represent an immutable reference sequence for a taxon.

    A reference sequence represents a single chromosome, viral segment, plasmid, or
    other contiguous DNA molecule belonging to a particular taxon. This can be an actual
    sequence or an artificial construct, typically then a consensus sequence. It can
    be used e.g. as a reference for alignment of other sequences or for optimising
    storage requirements of sequences. Any IUPAC ambiguity codes are allowed in the
    sequence.

    A reference sequence is immutable: once created, it cannot be deleted or updated.
    As such, reference sequence IDs can safely be referenced in other models and
    outside of the application.

    The ID of the reference sequence is equal to the hash of the sequence. As such, the
    ID of the reference sequence can be computed outside of the application as well.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_seqs",
        table_name="ref_seq",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links({1: ("taxon_id", Taxon, "taxon")}),
    )
    NAME: ClassVar = "RefSeq"

    code: str = Field(description="The code of the reference sequence", max_length=255)
    name: str = Field(description="The name of the reference sequence", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the reference sequence"
    )
    taxon_id: UUID = Field(description="The ID of the taxon. FOREIGN KEY")
    taxon: Taxon | None = Field(default=None, description="The taxon")
    genbank_accession_code: str | None = Field(
        default=None,
        description="The GenBank accession code of the reference sequence",
        max_length=255,
    )
