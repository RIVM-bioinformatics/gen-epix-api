import hashlib
import json
from functools import cached_property
from typing import Annotated, Any, ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model, validate_int_enum_value_or_none
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.fastapp.domain.util import create_multi_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.file import File
from gen_epix.seqdb.domain.model.seq.base import BaseSeq, QualityMixin
from gen_epix.seqdb.domain.model.seq.protocol import Protocol
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.ref_seq import RefSeq
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample


class Contig(BaseSeq, QualityMixin):
    """
    A contiguous DNA sequence. Any IUPAC ambiguity codes are allowed in the sequence.
    A contig is not persistable on its own, but is meant to be part of other objects
    through composition.

    A contig has an id that is equal to the hash code that uniquely identifies it
    based on its sequence.

    A contig is immutable: once created, it cannot be updated. As such,
    contig IDs can safely be referenced in other models and outside of the application.
    """

    NAME: ClassVar = "Contig"

    @field_serializer("id", mode="plain")
    def _serialize_id(self, value: UUID | None) -> str | None:
        if isinstance(value, UUID):
            return str(value)
        return value


class Seq(Model, HasSampleMixin, QualityMixin):
    """
    A DNA sequence, typically representing an assembled genome or a part thereof. A
    sequence consists of one or more contiguous sequences (contigs).

    The actual sequence data need not be provided on creation of this instance, to
    allow for deferred upload and processing of the sequence data. The is_available
    property can be used to check whether the sequence data have been processed and
    added to the sequence as contigs.

    A sequence that is available, is also immutable: once created and the contigs have
    been added, it cannot be deleted or semantically updated. As such, sequence IDs can
    safely be referenced in other models and outside of the application. The
    representation of the contigs that make up the sequence may still be updated to e.g.
    optimize storage or performance, but the actual sequence data will not change.

    The sequence hash of the sequence can be computed outside of the application as
    well,  based on the sorted sequence hashes of the contigs that make up the
    sequence, thereby providing an easy way to search for existing exactly matching
    sequences.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seqs",
        table_name="seq",
        persistable=True,
        keys=create_keys(
            {
                1: ("sample_id", "read_set_id", "read_set2_id", "protocol_id"),
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("file_id", File, "file"),
                3: ("read_set_id", ReadSet, "read_set"),
                4: ("read_set2_id", ReadSet, "read_set2"),
                5: ("protocol_id", Protocol, "protocol"),
            }
        ),
        multi_links=create_multi_links([("content", RefSeq)]),
    )
    uri: str | None = Field(
        default=None, description="The URI of the sequence data, if available."
    )
    file_id: UUID | None = Field(
        default=None,
        description="The unique file identifier for the sequence data. FOREIGN KEY",
    )
    file: File | None = Field(
        default=None, description="The file representing the sequence data."
    )
    file_format: enum.SeqFileFormat | None = Field(
        default=None, description="The format of the sequence file."
    )
    file_compression: enum.FileCompression | None = Field(
        default=None, description="The compression of the sequence file."
    )
    file_hash: UUID | None = Field(
        default=None,
        description="The first 128 bits of the SHA256 hash of the uncompressed sequence file representation.",
    )
    read_set_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the single read set used to generate the assembly, if available. FOREIGN KEY",
    )
    read_set: ReadSet | None = Field(default=None, description="The read set.")
    read_set2_id: UUID | None = Field(
        default=None,
        description="The unique identifier for a potential second read set used to generate the assembly. FOREIGN KEY",
    )
    read_set2: ReadSet | None = Field(default=None, description="The second read set.")
    protocol_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the protocol used to generate the sequence from reads, if available. FOREIGN KEY",
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    contigs: list[Contig] = Field(
        default_factory=list,
        description="The contigs that make up the sequence. No duplicate contigs are allowed. If zero contigs are provided, the sequence is considered to be not available yet.",
    )
    seq_hash: UUID = Field(
        default=NULL_ID,
        description="The first 128 bits of the SHA256 hash of the sorted contig seq hashes concatenated together. If the sequence has no contigs, the null UUID is returned.",
    )
    code: str | None = Field(
        default=None,
        max_length=255,
        description="A code for the seq for further reference",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="Whether the sequence has its contigs processed and available."
    )
    @property
    def is_available(self) -> bool:
        """"""
        return len(self.contigs) > 0

    @computed_field(  # type: ignore[prop-decorator]
        description="The number of contigs in the sequence. Zero if not available."
    )
    @cached_property
    def n_contigs(self) -> int:
        """"""
        return len(self.contigs)

    @computed_field(  # type: ignore[prop-decorator]
        description="The total length of all contigs in the sequence. Zero if not available."
    )
    @cached_property
    def length(self) -> int:
        """"""
        return sum(contig.length for contig in self.contigs) if self.contigs else 0

    @computed_field(  # type: ignore[prop-decorator]
        description="The length of the longest contig in the sequence. Zero if not available."
    )
    @cached_property
    # TODO: consider making this a computed field, add similar fields
    def max_contig_length(self) -> int:
        """"""
        return max(contig.length for contig in self.contigs) if self.contigs else 0

    @computed_field(  # type: ignore[prop-decorator]
        description="The length of the shortest contig in the sequence. Zero if not available."
    )
    @cached_property
    def min_contig_length(self) -> int:
        """"""
        return min(contig.length for contig in self.contigs) if self.contigs else 0

    @computed_field(  # type: ignore[prop-decorator]
        description="The median length of the contigs in the sequence. Zero if not available."
    )
    @cached_property
    def median_contig_length(self) -> float:
        """"""
        if not self.contigs:
            return 0.0
        lengths = sorted(contig.length for contig in self.contigs)
        n = len(lengths)
        if n % 2 == 0:
            return (lengths[n // 2 - 1] + lengths[n // 2]) / 2
        else:
            return float(lengths[n // 2])

    @computed_field(  # type: ignore[prop-decorator]
        description="The N50 of the sequence assembly. N50 is the length of the shortest contig such that the sum of contigs of this length or longer is at least 50% of the total assembly length. Zero if not available."
    )
    @cached_property
    def n50(self) -> int:
        """"""
        if not self.contigs:
            return 0
        # Sort contigs by length in descending order
        sorted_lengths = sorted(
            (contig.length for contig in self.contigs), reverse=True
        )
        # Calculate 50% of total assembly length
        half_total = self.length / 2
        # Find the breakpoint where cumulative sum reaches 50%
        cumulative_sum = 0
        for length in sorted_lengths:
            cumulative_sum += length
            if cumulative_sum >= half_total:
                return length
        raise RuntimeError("Unreachable code reached in n50 calculation")

    @field_validator("file_format", mode="before")
    @classmethod
    def _validate_file_format(
        cls, value: enum.SeqFileFormat | str | int | None
    ) -> enum.SeqFileFormat | None:
        return validate_int_enum_value_or_none(enum.SeqFileFormat, value)  # type: ignore[return-value]

    @field_validator("file_compression", mode="before")
    @classmethod
    def _validate_file_compression(
        cls, value: enum.FileCompression | str | int | None
    ) -> enum.FileCompression | None:
        return validate_int_enum_value_or_none(enum.FileCompression, value)  # type: ignore[return-value]

    @field_validator("contigs", mode="before")
    @classmethod
    def _validate_contigs(cls, value: list[Contig] | str) -> list[Contig]:
        """"""
        if isinstance(value, str):
            value = [Contig.model_validate(x) for x in json.loads(value)]
        elif isinstance(value, list):
            # Convert dict objects to Contig model instances if needed
            converted_value = []
            for item in value:
                if isinstance(item, dict):
                    converted_value.append(Contig.model_validate(item))
                else:
                    converted_value.append(item)
            value = converted_value
        # Check for duplicate contig sequences
        seen_hashes = set()
        for contig in value:
            if contig.id in seen_hashes:
                raise ValueError(f"Duplicate contig with hash/id {contig.id} found")
            seen_hashes.add(contig.id)
        return value

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """"""
        if self.file_id is not None:
            if self.file_format is None:
                raise ValueError("file_format must be provided when linking a file")
            if self.file_compression is None:
                self.file_compression = enum.FileCompression.NONE
        if self.uri is not None and self.file_id is not None:
            raise ValueError("Cannot have both uri and file_id")
        if self.read_set_id is None:
            if self.read_set2_id is not None:
                raise ValueError(
                    "Cannot have read_set2_id if read_set_id is not provided"
                )
        elif self.read_set2_id == self.read_set_id:
            raise ValueError("read_set2_id must be different from read_set_id")
        if self.seq_hash == NULL_ID and self.contigs:
            contig_hashes_bytes = sorted(x.id.bytes for x in self.contigs)
            concatenated = b"".join(contig_hashes_bytes)
            self.seq_hash = UUID(hashlib.sha256(concatenated).digest()[:16].hex())
        return self

    @field_serializer("contigs")
    def _serialize_contigs(self, value: list[Contig]) -> str:
        """"""
        return json.dumps([contig.model_dump() for contig in value])

    @staticmethod
    def get_nucleotide_seq_from_nextclade_format(
        ref_seq: str, nextclade_dict: dict[str, Any]
    ) -> str:
        """
        Convert a sequence represented in Nextclade format versus a particular reference
        sequence to the corresponding nucleotide sequence.
        """
        # Initialise sequence as list of reference sequence symbols
        seq = list(ref_seq)
        # Process substitutions
        substitutions = nextclade_dict.get("substitutions")
        if substitutions:
            for substitution in substitutions.split(","):
                reference_nucleotide = substitution[0].lower()
                position = int(substitution[1:-1])
                mutated_nucleotide = substitution[-1].lower()
                if seq[position - 1] != reference_nucleotide:
                    raise ValueError(
                        "Provided reference sequence does not match with reference positions encoded in substitutions at position {:d}: {:s} provided, found {:s}".format(
                            position,
                            seq[position - 1].upper(),
                            reference_nucleotide.upper(),
                        )
                    )
                seq[position - 1] = mutated_nucleotide.lower()
        # Process non-ACTGNs
        nonACGTN_ranges = nextclade_dict.get("non_acgtns")
        if nonACGTN_ranges:
            for nonACGTN_range in nonACGTN_ranges.split(","):
                nonACGTN = nonACGTN_range[0]
                nonACGTN_range = nonACGTN_range[2:].split("-")
                nonACGTN_start = int(nonACGTN_range[0])
                if len(nonACGTN_range) == 2:
                    nonACGTN_end = int(nonACGTN_range[1])
                else:
                    nonACGTN_end = nonACGTN_start
                for j in range(nonACGTN_start, nonACGTN_end + 1):
                    seq[j - 1] = nonACGTN.lower()
        # Process missings
        missing_ranges = nextclade_dict.get("missings")
        if missing_ranges:
            for missing_range in missing_ranges.split(","):
                missing_range = missing_range.split("-")
                missing_start = int(missing_range[0])
                if len(missing_range) == 2:
                    missing_end = int(missing_range[1])
                else:
                    missing_end = missing_start
                for j in range(missing_start, missing_end + 1):
                    seq[j - 1] = "n"
        # Process deletions
        deletion_ranges = nextclade_dict.get("deletions")
        if deletion_ranges:
            for deletion_range in deletion_ranges.split(","):
                deletion_range = deletion_range.split("-")
                deletion_start = int(deletion_range[0])
                if len(deletion_range) == 2:
                    deletion_end = int(deletion_range[1])
                else:
                    deletion_end = deletion_start
                for j in range(deletion_start, deletion_end + 1):
                    seq[j - 1] = ""
        # Process insertions
        insertions = nextclade_dict.get("insertions")
        if insertions:
            for insertion in insertions.split(","):
                position = int(insertion.split(":")[0])
                inserted_symbols = insertion.split(":")[1]
                seq[position - 1] = seq[position - 1] + inserted_symbols.lower()
        # Process alignment_start
        alignment_start = nextclade_dict.get("alignment_start")
        if alignment_start:
            for j in range(1, int(alignment_start)):
                seq[j - 1] = ""
        # Process alignment_end
        alignment_end = nextclade_dict.get("alignment_end")
        if alignment_end:
            j = int(alignment_end) + 1
            while j <= len(seq):
                seq[j - 1] = ""
                j = j + 1
        return "".join(seq)


class SeqIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        Seq,
        relationship_field_name="seq",
        snake_case_plural_name="seq_identifiers",
        table_name="seq_identifier",
    )
    NAME: ClassVar = "SeqIdentifier"
    MODEL_CLASS: ClassVar = Seq

    seq: Seq | None = Field(
        default=None, description="The sequence associated with this identifier."
    )


class HasSeqMixin:
    # Annotation-only: an assigned Field lingers as class attr -> pydantic shadow warning
    seq_id: Annotated[
        UUID | None,
        Field(
            default=None,
            description="The unique identifier for the sequence from which these results were obtained. FOREIGN KEY",
        ),
    ]
    seq: Annotated[Seq | None, Field(default=None, description="The sequence.")]
