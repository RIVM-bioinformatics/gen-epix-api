# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import hashlib
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.common.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import (
    AlignmentMixin,
    CodeMixin,
    ProtocolMixin,
    QualityMixin,
    SeqMixin,
)
from gen_epix.seqdb.domain.model.seq.metadata import (
    AlignmentProtocol,
    AssemblyProtocol,
    AstProtocol,
    KmerDetectionProtocol,
    LibraryPrepProtocol,
    Locus,
    LocusDetectionProtocol,
    LocusSet,
    PcrProtocol,
    RefSeq,
    SeqCategory,
    SeqClassificationProtocol,
    SnpDetectionProtocol,
    Taxon,
    TaxonomyProtocol,
)

_SERVICE_TYPE = enum.ServiceType.SEQ
_ENTITY_KWARGS = {
    "service_type": _SERVICE_TYPE,
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class Allele(Model, SeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alleles",
        table_name="allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "seq_hash_sha256")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
        **_ENTITY_KWARGS,
    )
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")


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
        **_ENTITY_KWARGS,
    )
    ref_allele_id: UUID
    ref_allele: Allele | None = Field(default=None, description="The reference allele.")
    allele_id: UUID
    allele: Allele | None = Field(default=None, description="The allele.")
    alignment_protocol_id: UUID = Field(
        description="The unique identifier for the sequence alignment protocol. FOREIGN KEY"
    )
    alignment_protocol: AlignmentProtocol | None = Field(
        default=None, description="The sequence alignment protocol."
    )


class Sample(Model, CodeMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="samples",
        table_name="sample",
        persistable=True,
        keys=create_keys({1: "code"}),
        **_ENTITY_KWARGS,
    )
    props: dict[str, str] = Field(
        default_factory=dict, description="The properties of the sample."
    )


class ReadSet(Model, CodeMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="read_sets",
        table_name="read_set",
        persistable=True,
        keys=create_keys({1: "code", 2: ("uri", "uri2")}),
        links=create_links(
            {
                1: (
                    "library_prep_protocol_id",
                    LibraryPrepProtocol,
                    "library_prep_protocol",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    uri: str = Field(description="The URI of the read set.")
    uri2: str | None = Field(
        default=None, description="The URI of the second paired read set, if any."
    )
    reads_hash_sha256: bytes | None = Field(
        description="The SHA256 hash of the uncompressed FASTQ file representation of the read set defined by uri.",
        min_length=32,
        max_length=32,
    )
    reads2_hash_sha256: bytes | None = Field(
        description="The SHA256 hash of the uncompressed FASTQ file representation of the read set defined by uri2.",
        min_length=32,
        max_length=32,
    )
    library_prep_protocol_id: UUID = Field(
        description="The unique identifier for the library preparation protocol. FOREIGN KEY"
    )
    library_prep_protocol: LibraryPrepProtocol | None = Field(
        default=None, description="The sequencing protocol."
    )
    sequencing_run_code: str | None = Field(
        description="The code of the sequencing run.", max_length=255
    )


class RawSeq(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="raw_seqs",
        table_name="raw_seq",
        persistable=True,
        **_ENTITY_KWARGS,
    )


class Seq(Model, CodeMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seqs",
        table_name="seq",
        persistable=True,
        keys=create_keys(
            {
                1: "code",
                2: (
                    "read_set_id",
                    "read_set2_id",
                    "assembly_protocol_id",
                    "raw_seq_id",
                ),
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
        **_ENTITY_KWARGS,
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


class ContigAlignment(Model, AlignmentMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="contig_alignments",
        persistable=False,
        **_ENTITY_KWARGS,
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
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq = Field(default=None, description="The sequence.")
    alignment_protocol_id: UUID = Field(
        description="The unique identifier for the sequence alignment protocol. FOREIGN KEY"
    )
    alignment_protocol: AlignmentProtocol | None = Field(
        default=None, description="The sequence alignment protocol."
    )
    contig_alignments: list[ContigAlignment] = Field(
        description="The contig alignments."
    )


class AlleleProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
        table_name="allele_profile",
        persistable=True,
        keys=create_keys(
            {1: ("seq_id", "locus_set_id", "locus_detection_protocol_id")}
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("locus_set_id", LocusSet, "locus_set"),
                3: (
                    "locus_detection_protocol_id",
                    LocusDetectionProtocol,
                    "locus_detection_protocol",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    locus_detection_protocol_id: UUID = Field(
        description="The unique identifier for the locus detection protocol. FOREIGN KEY"
    )
    locus_detection_protocol: LocusDetectionProtocol | None = Field(
        default=None, description="The locus detection protocol."
    )
    n_loci: int = Field(description="The number of loci detected.")
    allele_profile: str = Field(
        description="The alleles detected in the sequence for the loci in the locus set."
    )
    allele_profile_format: enum.AlleleProfileFormat = Field(
        default=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
        description="The representation format of the alleles.",
    )
    allele_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the sorted list of allele ids as bytes.",
        min_length=32,
        max_length=32,
    )

    @field_validator("allele_profile_hash_sha256", mode="before")
    def _validate_allele_profile_hash_sha256(cls, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return value

    @staticmethod
    def get_allele_profile_hash_sha256(allele_ids: list[UUID | None]) -> bytes:
        sha256 = hashlib.sha256()
        sha256.update(b"".join(sorted([x.bytes for x in allele_ids if x is not None])))
        return sha256.digest()

    @field_serializer("allele_profile_format")
    def _serialize_snp_profile_format(
        self, value: str | enum.AlleleProfileFormat
    ) -> str:
        if isinstance(value, enum.AlleleProfileFormat):
            return value.value
        return value


class SnpProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_profiles",
        table_name="snp_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "ref_seq_id",
                    "snp_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("ref_seq_id", RefSeq, "ref_seq"),
                3: (
                    "snp_detection_protocol_id",
                    SnpDetectionProtocol,
                    "snp_detection_protocol",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    snp_detection_protocol_id: UUID = Field(
        description="The unique identifier for the SNP detection protocol. FOREIGN KEY"
    )
    snp_detection_protocol: SnpDetectionProtocol | None = Field(
        default=None, description="The SNP detection protocol."
    )
    snp_profile: str = Field(description="The SNPs detected in the sequence.")
    snp_profile_format: enum.SnpProfileFormat = Field(
        default=enum.SnpProfileFormat.REF_ALN_SEQ,
        description="The representation format of the SNPs.",
    )
    snp_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII lower case reference sequence with all SNPs applied.",
        min_length=32,
        max_length=32,
    )

    @field_validator("snp_profile_hash_sha256", mode="before")
    def _validate_snp_profile_hash_sha256(cls, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return value

    @field_serializer("snp_profile_format")
    def _serialize_snp_profile_format(self, value: str | enum.SnpProfileFormat) -> str:
        if isinstance(value, enum.SnpProfileFormat):
            return value.value
        return value


class KmerProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_profiles",
        table_name="kmer_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "kmer_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "kmer_detection_protocol_id",
                    KmerDetectionProtocol,
                    "kmer_detection_protocol",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    kmer_detection_protocol_id: UUID = Field(
        description="The unique identifier for the k-mer detection protocol. FOREIGN KEY"
    )
    kmer_detection_protocol: KmerDetectionProtocol | None = Field(
        default=None, description="The k-mer detection protocol."
    )
    kmer_profile: str = Field(
        description="The k-mers detected in the sequence and their frequency."
    )
    kmer_profile_format: enum.KmerProfileFormat = Field(
        default=enum.KmerProfileFormat.KMER_PROFILE_FORMAT1,
        description="The representation format of the k-mers.",
    )
    kmer_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII sorted k-mers followed by their sorted frequencies as double precision floats.",
        min_length=32,
        max_length=32,
    )


class SeqClassification(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_classifications",
        table_name="seq_classification",
        persistable=True,
        keys=create_keys({1: ("seq_id", "seq_classification_protocol_id")}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "seq_classification_protocol_id",
                    SeqClassificationProtocol,
                    "seq_classification_protocol",
                ),
                3: ("primary_category_id", SeqCategory, "primary_category"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    seq_classification_protocol_id: UUID = Field(
        description="The ID of the sequence classification protocol. FOREIGN KEY"
    )
    seq_classification_protocol: SeqClassificationProtocol = Field(
        default=None, description="The sequence classification protocol."
    )
    primary_category_id: UUID | None = Field(
        description="The ID of the category. FOREIGN KEY"
    )
    primary_category: SeqCategory = Field(
        default=None, description="The primary category."
    )
    classification: str = Field(description="The classification of the sequence.")
    classification_format: enum.SeqClassificationFormat = Field(
        default=enum.SeqClassificationFormat.SEQ_CLASSIFICATION_FORMAT1,
        description="The representation format of the classification.",
    )
    classification_hash_sha256: bytes = Field(
        description="The SHA256 hash of the sorted list of category ids as bytes.",
        min_length=32,
        max_length=32,
    )


class SeqTaxonomy(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_taxonomies",
        table_name="seq_taxonomy",
        persistable=True,
        keys=create_keys({1: "seq_id", 2: "taxonomy_protocol_id"}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("taxonomy_protocol_id", TaxonomyProtocol, "taxonomy_protocol"),
                3: ("primary_taxon_id", Taxon, "primary_taxon"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    taxonomy_protocol_id: UUID = Field(
        description="The unique identifier for the taxonomy protocol. FOREIGN KEY"
    )
    taxonomy_protocol: TaxonomyProtocol | None = Field(
        default=None, description="The taxonomy protocol."
    )
    primary_taxon_id: UUID = Field(
        description="The unique identifier for the primary taxon. FOREIGN KEY"
    )
    primary_taxon: UUID = Field(default=None, description="The primary taxon.")
    taxonomy: str = Field(description="The taxonomy results of the sequence.")
    taxonomy_format: enum.TaxonomyFormat = Field(
        default=enum.TaxonomyFormat.TAXONOMY_FORMAT1,
        description="The representation format of the taxonomy.",
    )
    taxonomy_hash_sha256: bytes = Field(
        description="The SHA256 hash of the sorted list of taxon ids as bytes.",
        min_length=32,
        max_length=32,
    )


class PcrMeasurement(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="pcr_measurements",
        table_name="pcr_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "pcr_protocol_id", "index")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("pcr_protocol_id", PcrProtocol, "pcr_protocol"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    sample_id: UUID = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    pcr_protocol_id: UUID = Field(
        description="The unique identifier for the PCR protocol. FOREIGN KEY"
    )
    pcr_protocol: PcrProtocol | None = Field(
        default=None, description="The PCR protocol."
    )
    pcr_result: str = Field(description="The result of the PCR experiment.")
    pcr_result_format: enum.PcrResultFormat = Field(
        default=enum.PcrResultFormat.PCR_RESULT_FORMAT1,
        description="The representation format of the PCR result.",
    )
    index: int = Field(default=1, description="The index of the measurement.")


class AstMeasurement(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_measurements",
        table_name="ast_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "ast_protocol_id", "index")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("ast_protocol_id", AstProtocol, "ast_protocol"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    sample_id: UUID = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    ast_protocol_id: UUID = Field(
        description="The unique identifier for the AST protocol. FOREIGN KEY"
    )
    ast_protocol: AstProtocol | None = Field(
        default=None, description="The AST protocol."
    )
    ast_result: str = Field(description="The result of the AST experiment.")
    ast_result_format: enum.AstResultFormat = Field(
        default=enum.AstResultFormat.AST_RESULT_FORMAT1,
        description="The representation format of the AST result.",
    )
    index: int = Field(default=1, description="The index of the measurement.")


class AstPrediction(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_predictions",
        table_name="ast_prediction",
        persistable=True,
        keys=create_keys({1: ("seq_id", "ast_protocol_id")}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("ast_protocol_id", AstProtocol, "ast_protocol"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    ast_protocol_id: UUID = Field(
        description="The unique identifier for the AST protocol. FOREIGN KEY"
    )
    ast_protocol: AstProtocol | None = Field(
        default=None, description="The AST protocol."
    )
    ast_result: str = Field(description="The result of the AST prediction.")
    ast_result_format: enum.AstResultFormat = Field(
        default=enum.AstResultFormat.AST_RESULT_FORMAT1,
        description="The representation format of the AST result.",
    )


class SeqDistanceProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distance_protocols",
        table_name="seq_distance_protocol",
        persistable=True,
        keys=create_keys(
            {
                1: "code",
                2: ("name", "version"),
                3: ("seq_distance_protocol_type", "locus_set_id", "ref_seq_id"),
            }
        ),
        links=create_links(
            {
                1: ("locus_set_id", LocusSet, "locus_set"),
                2: ("ref_seq_id", RefSeq, "ref_seq"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    max_stored_distance: float = Field(description="The maximum distance to be stored")
    min_scale_unit: float = Field(description="The minimum unit to be shown in a scale")
    seq_distance_protocol_type: enum.SeqDistanceProtocolType
    locus_set_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the locus set, if applicable. FOREIGN KEY",
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    ref_seq_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the reference sequence, if applicable. FOREIGN KEY",
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.ALLELE_BASED.value
            and self.locus_set_id is None
        ):
            raise ValueError("locus_set_id must be provided for allele based type")
        elif (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.SNP_BASED.value
            and self.ref_seq_id is None
        ):
            raise ValueError("ref_seq_id must be provided for snp based type")
        return self

    @field_serializer("seq_distance_protocol_type")
    def _serialize_seq_format(self, value: str | enum.SeqDistanceProtocolType) -> str:
        if isinstance(value, enum.SeqDistanceProtocolType):
            return value.value
        return value


class SeqDistance(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distances",
        table_name="seq_distance",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "seq_distance_protocol_id",
                    "allele_profile_id",
                    "snp_profile_id",
                    "kmer_profile_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "seq_distance_protocol_id",
                    SeqDistanceProtocol,
                    "seq_distance_protocol",
                ),
                3: ("allele_profile_id", AlleleProfile, "allele_profile"),
                4: ("snp_profile_id", SnpProfile, "snp_profile"),
                5: ("kmer_profile_id", KmerProfile, "kmer_profile"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    seq_distance_protocol_id: UUID = Field(
        description="The unique identifier for the genetic distance protocol. FOREIGN KEY"
    )
    seq_distance_protocol: SeqDistanceProtocol | None = Field(
        default=None, description="The genetic distance protocol."
    )
    allele_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the allele profile, if applicable. FOREIGN KEY",
    )
    allele_profile: AlleleProfile | None = Field(
        default=None, description="The allele profile."
    )
    snp_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the SNP profile, if applicable. FOREIGN KEY",
    )
    snp_profile: SnpProfile | None = Field(default=None, description="The SNP profile.")
    kmer_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the k-mer profile, if applicable. FOREIGN KEY",
    )
    kmer_profile: SnpProfile | None = Field(
        default=None, description="The k-mer profile."
    )
    distance_format: enum.SeqDistanceFormat = Field(
        default=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
        description="The representation format of the distances.",
    )
    distances: str = Field(description="The distances to other sequences.")

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        ids = [self.allele_profile_id, self.snp_profile_id, self.kmer_profile_id]
        has_ids = [x is not None for x in ids]
        if not any(has_ids):
            raise ValueError(
                "Either allele_profile_id, snp_profile_id or kmer_profile_id must be provided"
            )
        elif sum(has_ids) > 1:
            raise ValueError(
                "Only one of allele_profile_id, snp_profile_id or kmer_profile_id must be provided"
            )
        objs = [self.allele_profile, self.snp_profile, self.kmer_profile]
        for has_id, obj in zip(has_ids, objs):
            if not has_id and obj is not None:
                raise ValueError(f"{obj.__class__.__name__} must be None")
        return self

    @field_serializer("distance_format")
    def _serialize_distance_format(self, value: str | enum.SeqDistanceFormat) -> str:
        if isinstance(value, enum.SeqDistanceFormat):
            return value.value
        return value
