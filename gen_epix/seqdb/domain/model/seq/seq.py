from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import (
    CodeMixin,
    ProtocolMixin,
    QualityMixin,
    SeqMixin,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.sample import Sample
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class RawSeq(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="raw_seqs",
        table_name="raw_seq",
        persistable=True,
    )


class AssemblyProtocol(Model, ProtocolMixin):
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


class Seq(Model, CodeMixin, QualityMixin):
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
                2: ("read_set_id", ReadSet, "read_set"),
                3: ("read_set2_id", ReadSet, "read_set2"),
                4: ("assembly_protocol_id", AssemblyProtocol, "assembly_protocol"),
                5: ("raw_seq_id", RawSeq, "raw_seq"),
            }
        ),
    )
    sample_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the sample, if available. FOREIGN KEY",
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    read_set_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the single read set used to generate the assembly, if available. FOREIGN KEY",
    )
    read_set: ReadSet | None = Field(default=None, description="The read set.")
    read_set2_id: UUID | None = Field(
        default=None,
        description="The unique identifier for a second read set used to generate the assembly, if more than one. FOREIGN KEY",
    )
    read_set2: ReadSet | None = Field(default=None, description="The second read set.")
    assembly_protocol_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the assembly protocol, if available. FOREIGN KEY",
    )
    assembly_protocol: AssemblyProtocol | None = Field(
        default=None, description="The assembly protocol."
    )
    raw_seq_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the raw sequence, if available. FOREIGN KEY",
    )
    raw_seq: RawSeq | None = Field(default=None, description="The raw sequence.")
    file_id: UUID | None = Field(
        default=None, description="The unique file identifier."
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.read_set_id is None:
            if self.read_set2_id is not None:
                raise ValueError(
                    "read_set2_id may only be provided if read_set_id is provided"
                )
        elif self.read_set2_id == self.read_set_id:
            raise ValueError("read_set2_id must be different from read_set_id")
        return self


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


class RefSeq(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_seqs",
        table_name="ref_seq",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links({1: ("taxon_id", Taxon, "taxon")}),
    )
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
