from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain.model.seq.base import (
    AlignmentMixin,
    ProtocolMixin,
    QualityMixin,
)
from gen_epix.seqdb.domain.model.seq.locus import Allele
from gen_epix.seqdb.domain.model.seq.seq import Seq


class AlignmentProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alignment_protocols",
        table_name="alignment_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )
    is_multiple: bool = Field(
        description="Whether the alignment protocol can be used for more than two sequences"
    )


class AlleleAlignment(Model, AlignmentMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_alignments",
        table_name="allele_alignment",
        persistable=True,
        keys=create_keys({1: ("ref_allele_id", "allele_id", "alignment_protocol_id")}),
        links=create_links(
            {
                1: ("ref_allele_id", Allele, "ref_allele"),
                2: ("allele_id", Allele, "allele"),
                3: (
                    "alignment_protocol_id",
                    AlignmentProtocol,
                    "alignment_protocol",
                ),
            }
        ),
    )
    ref_allele_id: UUID = Field(
        description="The unique identifier for the reference allele. FOREIGN KEY"
    )
    ref_allele: Allele | None = Field(default=None, description="The reference allele.")
    allele_id: UUID = Field(
        description="The unique identifier for the allele. FOREIGN KEY"
    )
    allele: Allele | None = Field(default=None, description="The allele.")
    alignment_protocol_id: UUID = Field(
        description="The unique identifier for the sequence alignment protocol. FOREIGN KEY"
    )
    alignment_protocol: AlignmentProtocol | None = Field(
        default=None, description="The sequence alignment protocol."
    )


class ContigAlignment(Model, AlignmentMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="contig_alignments",
        persistable=False,
    )
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )


class SeqAlignment(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_alignments",
        table_name="seq_alignment",
        persistable=True,
        keys=create_keys({1: ("seq_id", "alignment_protocol_id")}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "alignment_protocol_id",
                    AlignmentProtocol,
                    "alignment_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
    )
    seq: Seq = Field(description="The sequence.")
    alignment_protocol_id: UUID = Field(
        description="The unique identifier for the sequence alignment protocol. FOREIGN KEY"
    )
    alignment_protocol: AlignmentProtocol | None = Field(
        default=None, description="The sequence alignment protocol."
    )
    contig_alignments: list[ContigAlignment] = Field(
        description="The contig alignments."
    )


class MultipleAlignment(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="multiple_alignments",
        persistable=False,
    )
    alignment_protocol_id: UUID = Field(
        description="The ID of the alignment protocol. FOREIGN KEY"
    )
    seq_ids: list[UUID] = Field(
        description="The list of sequence IDs included in the multiple alignment."
    )
    n_seqs: int = Field(description="The number of sequences in the alignment.")
    n_contigs: list[int] = Field(
        description="The number of contigs for each sequence in the alignment."
    )
    contig_seqs: list[list[str]] = Field(
        description="The list of contig sequences for each sequence in the alignment."
    )
    n_alignments: int = Field(description="The number of alignments.")
    n_columns: list[int] = Field(
        description="The number of columns for each alignment."
    )
    start_columns: list[list[int]] = Field(
        description="The start column positions for each alignment."
    )
    contig_ordinals: list[list[int]] = Field(
        description="The ordinals of the contigs for each sequence in the alignment."
    )
    contig_start_positions: list[list[int]] = Field(
        description="The start positions of the contigs for each sequence in the alignment."
    )
    contig_directions: list[list[bool]] = Field(
        description="The directions of the contigs for each sequence in the alignment."
    )
    lengths: list[list[int]] = Field(
        description="The lengths of the contigs for each sequence in the alignment."
    )
