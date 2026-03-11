# pylint: disable=too-few-public-methods

from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, relationship

from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.commondb.repositories.sa_model.organization import IdentifierMixin
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.base import (
    AlignmentMixin,
    CodeMixin,
    ProtocolMixin,
    QualityMixin,
    SeqMixin,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SEQ.value)

# TODO: add SA relationship calls


class Allele(Base, RowMetadataMixin, SeqMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Allele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Allele, "locus_id")


class AlleleAlignment(Base, RowMetadataMixin, AlignmentMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AlleleAlignment)

    ref_allele_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleAlignment, "ref_allele_id"
    )
    allele_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleAlignment, "allele_id"
    )
    alignment_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleAlignment, "alignment_protocol_id"
    )


class AlleleProfile(Base, RowMetadataMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AlleleProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "seq_id"
    )
    locus_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "locus_set_id"
    )
    locus_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "locus_detection_protocol_id"
    )
    n_loci: Mapped[int] = create_mapped_column(DOMAIN, model.AlleleProfile, "n_loci")
    allele_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "allele_profile"
    )
    allele_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "allele_profile_format"
    )
    allele_profile_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "allele_profile_hash"
    )


class AlleleProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AlleleProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfileIdentifier, "internal_id"
    )
    allele_profile: Mapped[AlleleProfile] = relationship(
        AlleleProfile, foreign_keys=[internal_id]
    )


class AlignmentProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AlignmentProtocol)

    is_multiple: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AlignmentProtocol, "is_multiple"
    )


class AssemblyProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AssemblyProtocol)

    has_manual_curation: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AssemblyProtocol, "has_manual_curation"
    )


class AstMeasurement(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AstMeasurement)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "sample_id"
    )
    ast_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "ast_protocol_id"
    )
    ast_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "ast_result"
    )
    ast_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "ast_result_format"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.AstMeasurement, "index")


class AstPrediction(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AstPrediction)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstPrediction, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.AstPrediction, "seq_id"
    )
    ast_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_protocol_id"
    )
    ast_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result"
    )
    ast_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result_format"
    )


class AstProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AstProtocol)

    antimicrobial_names: Mapped[list[str]] = create_mapped_column(
        DOMAIN, model.AstProtocol, "antimicrobial_names"
    )
    is_predicted: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AstProtocol, "is_predicted"
    )


class KmerDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.KmerDetectionProtocol)


class KmerProfile(Base, RowMetadataMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.KmerProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfile, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.KmerProfile, "seq_id"
    )
    kmer_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_detection_protocol_id"
    )
    kmer_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile"
    )
    kmer_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile_format"
    )
    kmer_profile_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile_hash"
    )


class KmerProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.KmerProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfileIdentifier, "internal_id"
    )
    kmer_profile: Mapped[KmerProfile] = relationship(
        KmerProfile, foreign_keys=[internal_id]
    )


class Locus(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Locus)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Locus, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Locus, "name")
    description: Mapped[str] = create_mapped_column(DOMAIN, model.Locus, "description")
    locus_type: Mapped[enum.LocusType] = create_mapped_column(
        DOMAIN, model.Locus, "locus_type"
    )
    gene_product_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.Locus, "gene_product_code"
    )


class LocusCodeMap(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.LocusCodeMap)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.LocusCodeMap, "code")
    code_map: Mapped[dict[str, UUID]] = create_mapped_column(
        DOMAIN, model.LocusCodeMap, "code_map"
    )


class LocusDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.LocusDetectionProtocol)


class LocusProfile(Base, RowMetadataMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.LocusProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfile, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.LocusProfile, "seq_id"
    )
    locus_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfile, "locus_set_id"
    )
    locus_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfile, "locus_detection_protocol_id"
    )
    n_loci: Mapped[int] = create_mapped_column(DOMAIN, model.LocusProfile, "n_loci")
    locus_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.LocusProfile, "locus_profile"
    )
    locus_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.LocusProfile, "locus_profile_format"
    )
    locus_profile_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfile, "locus_profile_hash"
    )


class LocusProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.LocusProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfileIdentifier, "internal_id"
    )
    locus_profile: Mapped[LocusProfile] = relationship(
        LocusProfile, foreign_keys=[internal_id]
    )


class LocusSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.LocusSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.LocusSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.LocusSet, "name")
    n_loci: Mapped[int] = create_mapped_column(DOMAIN, model.LocusSet, "n_loci")
    locus_ids: Mapped[list[UUID]] = create_mapped_column(
        DOMAIN, model.LocusSet, "locus_ids"
    )


class MlvaDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.MlvaDetectionProtocol)


class MlvaProfile(Base, RowMetadataMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.MlvaProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "seq_id"
    )
    mlva_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "mlva_detection_protocol_id"
    )
    locus_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "locus_set_id"
    )
    mlva_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "mlva_profile"
    )
    mlva_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "mlva_profile_format"
    )
    mlva_profile_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "mlva_profile_hash"
    )


class MlvaProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.MlvaProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfileIdentifier, "internal_id"
    )
    mlva_profile: Mapped[MlvaProfile] = relationship(
        MlvaProfile, foreign_keys=[internal_id]
    )


class PcrMeasurement(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.PcrMeasurement)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "sample_id"
    )
    pcr_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "pcr_protocol_id"
    )
    pcr_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "pcr_result"
    )
    pcr_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "pcr_result_format"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.PcrMeasurement, "index")


class PcrProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.PcrProtocol)

    target_names: Mapped[list[str]] = create_mapped_column(
        DOMAIN, model.PcrProtocol, "target_names"
    )


class ReadSet(Base, RowMetadataMixin, CodeMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ReadSet)

    sample_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.ReadSet, "sample_id")
    fwd_uri: Mapped[str] = create_mapped_column(DOMAIN, model.ReadSet, "fwd_uri")
    rev_uri: Mapped[str] = create_mapped_column(DOMAIN, model.ReadSet, "rev_uri")
    fwd_file_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "fwd_file_id"
    )
    rev_file_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "rev_file_id"
    )
    file_format: Mapped[enum.ReadsFileFormat] = create_mapped_column(
        DOMAIN, model.ReadSet, "file_format"
    )
    file_compression: Mapped[enum.FileCompression] = create_mapped_column(
        DOMAIN, model.ReadSet, "file_compression"
    )
    fwd_reads_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "fwd_reads_hash"
    )
    rev_reads_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "rev_reads_hash"
    )
    sequencing_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "sequencing_protocol_id"
    )
    sequencing_run_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.ReadSet, "sequencing_run_code"
    )
    is_available: Mapped[bool] = create_mapped_column(
        DOMAIN, model.ReadSet, "is_available"
    )


class ReadSetIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ReadSetIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSetIdentifier, "internal_id"
    )
    read_set: Mapped[ReadSet] = relationship(ReadSet, foreign_keys=[internal_id])


class RefAllele(Base, RowMetadataMixin, SeqMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefAllele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.RefAllele, "locus_id")
    index: Mapped[int] = create_mapped_column(DOMAIN, model.RefAllele, "index")


class RefSeq(Base, RowMetadataMixin, SeqMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefSeq)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "name")
    description: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "description")
    taxon_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.RefSeq, "taxon_id")
    genbank_accession_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.RefSeq, "genbank_accession_code"
    )


class RefSnp(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefSnp)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "code")
    ref_seq_id: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "ref_seq_id")
    position: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "position")
    nucleotide: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "nucleotide")


class RefSnpSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefSnpSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnpSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnpSet, "name")


class RefSnpSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefSnpSetMember)

    ref_snp_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RefSnpSetMember, "ref_snp_set_id"
    )
    ref_snp_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RefSnpSetMember, "ref_snp_id"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.RefSnpSetMember, "index")


class Sample(Base, RowMetadataMixin, CodeMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Sample)

    created_in_data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Sample, "created_in_data_collection_id"
    )
    props: Mapped[dict[str, str]] = create_mapped_column(DOMAIN, model.Sample, "props")


class SampleDataCollectionLink(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SampleDataCollectionLink)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SampleDataCollectionLink, "sample_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SampleDataCollectionLink, "data_collection_id"
    )


class SampleIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SampleIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SampleIdentifier, "internal_id"
    )
    sample: Mapped[Sample] = relationship(Sample, foreign_keys=[internal_id])


class Seq(Base, RowMetadataMixin, CodeMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Seq)

    sample_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "sample_id")
    uri: Mapped[str] = create_mapped_column(DOMAIN, model.Seq, "uri")
    file_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "file_id")
    file_format: Mapped[enum.SeqFileFormat] = create_mapped_column(
        DOMAIN, model.Seq, "file_format"
    )
    file_compression: Mapped[enum.FileCompression] = create_mapped_column(
        DOMAIN, model.Seq, "file_compression"
    )
    file_hash: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "file_hash")
    read_set_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "read_set_id")
    read_set2_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "read_set2_id")
    assembly_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Seq, "assembly_protocol_id"
    )
    contigs: Mapped[list[model.Contig]] = create_mapped_column(
        DOMAIN, model.Seq, "contigs"
    )
    seq_hash: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "seq_hash")
    is_available: Mapped[bool] = create_mapped_column(DOMAIN, model.Seq, "is_available")
    n_contigs: Mapped[int] = create_mapped_column(DOMAIN, model.Seq, "n_contigs")
    length: Mapped[int] = create_mapped_column(DOMAIN, model.Seq, "length")
    max_contig_length: Mapped[int] = create_mapped_column(
        DOMAIN, model.Seq, "max_contig_length"
    )
    min_contig_length: Mapped[int] = create_mapped_column(
        DOMAIN, model.Seq, "min_contig_length"
    )
    median_contig_length: Mapped[float] = create_mapped_column(
        DOMAIN, model.Seq, "median_contig_length"
    )
    n50: Mapped[int] = create_mapped_column(DOMAIN, model.Seq, "n50")


class SeqIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqIdentifier, "internal_id"
    )
    seq: Mapped[Seq] = relationship(Seq, foreign_keys=[internal_id])


class SeqAlignment(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqAlignment)

    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SeqAlignment, "seq_id"
    )
    alignment_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqAlignment, "alignment_protocol_id"
    )
    contig_alignments: Mapped[list[model.ContigAlignment]] = create_mapped_column(
        DOMAIN, model.SeqAlignment, "contig_alignments"
    )


class SeqCategory(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqCategory)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "name")
    seq_category_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqCategory, "seq_category_set_id"
    )


class SeqCategorySet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqCategorySet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "name")


class SeqClassification(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqClassification)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SeqClassification, "seq_id"
    )
    seq_classification_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "seq_classification_protocol_id"
    )
    primary_category_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "primary_category_id"
    )
    classification: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqClassification, "classification"
    )
    classification_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqClassification, "classification_format"
    )
    classification_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "classification_hash"
    )


class SeqClassificationProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqClassificationProtocol)

    is_taxonomic: Mapped[bool] = create_mapped_column(
        DOMAIN, model.SeqClassificationProtocol, "is_taxonomic"
    )


class SeqDistance(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqDistance)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "sample_id"
    )
    seq_distance_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "seq_distance_protocol_id"
    )
    profile_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "profile_id"
    )
    distance_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqDistance, "distance_format"
    )
    distances: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqDistance, "distances"
    )


class SeqDistanceProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqDistanceProtocol)

    is_integer_distance: Mapped[bool] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "is_integer_distance"
    )
    seq_distance_protocol_type: Mapped[enum.SeqDistanceProtocolType] = (
        create_mapped_column(
            DOMAIN, model.SeqDistanceProtocol, "seq_distance_protocol_type"
        )
    )
    locus_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "locus_set_id"
    )
    ref_seq_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "ref_seq_id"
    )
    max_stored_distance: Mapped[float] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "max_stored_distance"
    )


class SeqTaxonomy(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqTaxonomy)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "seq_id"
    )
    taxonomy_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "taxonomy_protocol_id"
    )
    primary_taxon_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "primary_taxon_id"
    )
    taxonomy: Mapped[str] = create_mapped_column(DOMAIN, model.SeqTaxonomy, "taxonomy")
    taxonomy_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "taxonomy_format"
    )
    taxonomy_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "taxonomy_hash"
    )


class SequencingProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SequencingProtocol)


class SnpDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SnpDetectionProtocol)


class SnpProfile(Base, RowMetadataMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SnpProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "sample_id"
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SnpProfile, "seq_id"
    )
    ref_seq_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "ref_seq_id"
    )
    snp_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_detection_protocol_id"
    )
    snp_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile"
    )
    snp_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile_format"
    )
    snp_profile_hash: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile_hash"
    )


class SnpProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SnpProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfileIdentifier, "internal_id"
    )
    snp_profile: Mapped[SnpProfile] = relationship(
        SnpProfile, foreign_keys=[internal_id]
    )


class Taxon(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Taxon)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Taxon, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Taxon, "name")
    rank: Mapped[str] = create_mapped_column(DOMAIN, model.Taxon, "rank")
    ncbi_taxid: Mapped[int] = create_mapped_column(DOMAIN, model.Taxon, "ncbi_taxid")
    ictv_ictv_id: Mapped[str] = create_mapped_column(
        DOMAIN, model.Taxon, "ictv_ictv_id"
    )
    snomed_sctid: Mapped[int] = create_mapped_column(
        DOMAIN, model.Taxon, "snomed_sctid"
    )
    ncbi_ancestor_taxids: Mapped[list[int]] = create_mapped_column(
        DOMAIN, model.Taxon, "ncbi_ancestor_taxids"
    )
    ancestor_taxon_ids: Mapped[list[UUID]] = create_mapped_column(
        DOMAIN, model.Taxon, "ancestor_taxon_ids"
    )


class TaxonomyProtocol(Base, RowMetadataMixin, ProtocolMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.TaxonomyProtocol)


class TaxonSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.TaxonSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.TaxonSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.TaxonSet, "name")


class TaxonSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.TaxonSetMember)

    taxon_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonSetMember, "taxon_set_id"
    )
    taxon_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonSetMember, "taxon_id"
    )


class TreeAlgorithm(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.TreeAlgorithm)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.TreeAlgorithm, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.TreeAlgorithm, "name")
    description: Mapped[str] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "description"
    )
    tree_algorithm_class_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "tree_algorithm_class_id"
    )
    is_ultrametric: Mapped[bool] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "is_ultrametric"
    )
    rank: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.TreeAlgorithmClass, "rank"
    )


class TreeAlgorithmClass(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.TreeAlgorithmClass)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.TreeAlgorithmClass, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.TreeAlgorithmClass, "name")
    is_seq_based: Mapped[bool] = create_mapped_column(
        DOMAIN, model.TreeAlgorithmClass, "is_seq_based"
    )
    is_dist_based: Mapped[bool] = create_mapped_column(
        DOMAIN, model.TreeAlgorithmClass, "is_dist_based"
    )
    rank: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.TreeAlgorithmClass, "rank"
    )
