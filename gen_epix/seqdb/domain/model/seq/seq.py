import hashlib
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

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.file import File
from gen_epix.seqdb.domain.model.seq.base import (
    BaseSeq,
    CodeMixin,
    ProtocolMixin,
    QualityMixin,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class RefSeq(BaseSeq):
    """
    A reference sequence for a single chromosome, viral segment, plasmid or other
    contiguous DNA molecule belonging to a particular taxon. This can be an actual
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


class AssemblyProtocol(Model, ProtocolMixin):
    """
    A protocol used for assembling sequencing reads into a sequence.

    An assembly protocol is immutable: once created, it cannot be deleted and it
    should not be semantically updated. As such, assembly protocol IDs can safely be
    referenced in other models and outside of the application.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="assembly_protocols",
        table_name="assembly_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )
    has_manual_curation: bool = Field(
        default=False,
        description="Whether the assembly has a, potentially optional, manual curation step.",
    )


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


class Seq(Model, HasSampleMixin, CodeMixin, QualityMixin):
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
                1: "code",
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("file_id", File, "file"),
                3: ("read_set_id", ReadSet, "read_set"),
                4: ("read_set2_id", ReadSet, "read_set2"),
                5: ("assembly_protocol_id", AssemblyProtocol, "assembly_protocol"),
            }
        ),
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
    assembly_protocol_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the assembly protocol used to generate the sequence from reads, if available. FOREIGN KEY",
    )
    assembly_protocol: AssemblyProtocol | None = Field(
        default=None, description="The assembly protocol."
    )
    contigs: list[Contig] = Field(
        default_factory=list,
        description="The contigs that make up the sequence. No duplicate contigs are allowed. If zero contigs are provided, the sequence is considered to be not available yet.",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="Whether the sequence has its contigs processed and available."
    )
    @property
    def is_available(self) -> bool:
        """"""
        return len(self.contigs) > 0

    @computed_field(  # type: ignore[prop-decorator]
        description="The first 128 bits of the SHA256 hash of the sorted contig seq hashes concatenated together. If the sequence has no contigs, the null UUID is returned."
    )
    @cached_property
    def seq_hash(self) -> UUID:
        """"""
        if not self.contigs:
            return NULL_ID
        # Get sorted list of contig seq_hashes as bytes
        contig_hashes_bytes = sorted(x.id.bytes for x in self.contigs)
        # Concatenate the bytes
        concatenated = b"".join(contig_hashes_bytes)
        # Compute SHA256 hash and take first 16 bytes (128 bits)
        return UUID(hashlib.sha256(concatenated).digest()[:16].hex())

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
        cls, value: enum.SeqFileFormat | str | None
    ) -> enum.SeqFileFormat | None:
        if isinstance(value, str):
            return enum.SeqFileFormat(value)
        return value

    @field_validator("file_compression", mode="before")
    @classmethod
    def _validate_file_compression(
        cls, value: enum.FileCompression | str | None
    ) -> enum.FileCompression | None:
        if isinstance(value, str):
            return enum.FileCompression(value)
        return value

    @field_validator("contigs", mode="before")
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
        return self

    @field_serializer("contigs")
    def _serialize_contigs(self, value: list[Contig]) -> str:
        """"""
        return json.dumps([contig.model_dump() for contig in value])


class CompleteContig(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_contigs",
        persistable=False,
    )
    seq_id: UUID = Field(description="The ID of the sequence.")
    seq: str = Field(description="The contig sequence.")
    qc: enum.QualityControlResult = Field(
        description="The quality control result of the contig sequence."
    )
    index: int = Field(description="The index of the contig in the sequence.")


class RefSnp(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snps",
        table_name="ref_snp",
        persistable=True,
        keys=create_keys({1: "code", 2: ("ref_seq_id", "position", "nucleotide")}),
        links=create_links({1: ("ref_seq_id", RefSeq, "ref_seq")}),
    )
    code: str = Field(description="The code of the reference SNP.", max_length=255)
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    position: int = Field(description="The position of the reference SNP.")
    nucleotide: str = Field(
        description="The nucleotide of the reference SNP.", min_length=1, max_length=1
    )


class RefSnpSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snp_sets",
        table_name="ref_snp_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the reference SNP set.", max_length=255)
    name: str = Field(description="The name of the reference SNP set.", max_length=255)


class RefSnpSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snp_set_members",
        table_name="ref_snp_set_member",
        persistable=True,
        keys=create_keys(
            {
                1: ("ref_snp_set_id", "ref_snp_id"),
                2: ("ref_snp_set_id", "index"),
            }
        ),
        links=create_links(
            {
                1: ("ref_snp_set_id", RefSnpSet, "ref_snp_set"),
                2: ("ref_snp_id", RefSnp, "ref_snp"),
            }
        ),
    )
    ref_snp_set_id: UUID = Field(
        description="The unique identifier for the reference SNP set. FOREIGN KEY"
    )
    ref_snp_set: RefSnpSet | None = Field(
        default=None, description="The reference SNP set."
    )
    ref_snp_id: UUID = Field(
        description="The unique identifier for the reference SNP. FOREIGN KEY"
    )
    ref_snp: RefSnp | None = Field(default=None, description="The reference SNP.")
    index: int = Field(
        description="The index (ordinal number) of the reference SNP in the reference SNP set."
    )
