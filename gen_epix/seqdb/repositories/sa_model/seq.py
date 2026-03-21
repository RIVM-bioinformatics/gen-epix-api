# pylint: disable=too-few-public-methods
from datetime import date
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
    CodeMixin,
    QualityMixin,
    SeqMixin,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SEQ.value)


# TODO: add SA relationship calls


class Protocol(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Protocol)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Protocol, "code")
    name: Mapped[str | None] = create_mapped_column(DOMAIN, model.Protocol, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Protocol, "description"
    )
    protocol_type: Mapped[enum.ProtocolType] = create_mapped_column(
        DOMAIN, model.Protocol, "protocol_type"
    )
    git_repository_uri: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Protocol, "git_repository_uri"
    )
    git_commit_hash: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Protocol, "git_commit_hash"
    )
    git_commit_tag: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Protocol, "git_commit_tag"
    )
    valid_start_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_start_date"
    )
    valid_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_end_date"
    )
    ref_seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Protocol, "ref_seq_id"
    )
    seq_category_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Protocol, "seq_category_set_id"
    )
    locus_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Protocol, "locus_set_id"
    )
    seq_profile_type: Mapped[enum.SeqProfileType | None] = create_mapped_column(
        DOMAIN, model.Protocol, "seq_profile_type"
    )
    seq_distance_type: Mapped[enum.SeqDistanceType | None] = create_mapped_column(
        DOMAIN, model.Protocol, "seq_distance_type"
    )
    is_integer_distance: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Protocol, "is_integer_distance"
    )
    max_stored_distance: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Protocol, "max_stored_distance"
    )
    props: Mapped[dict[str, str | int | float | bool | list]] = create_mapped_column(
        DOMAIN, model.Protocol, "props"
    )


class Allele(Base, RowMetadataMixin, SeqMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Allele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Allele, "locus_id")


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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "protocol_id"
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


class AstMeasurement(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.AstMeasurement)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "sample_id"
    )
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstMeasurement, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstPrediction, "protocol_id"
    )
    ast_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result"
    )
    ast_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result_format"
    )


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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfile, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusProfile, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MlvaProfile, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "protocol_id"
    )
    pcr_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "pcr_result"
    )
    pcr_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.PcrMeasurement, "pcr_result_format"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.PcrMeasurement, "index")


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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "protocol_id")
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


class SeqCategory(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqCategory)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "name")
    seq_category_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN,
        model.SeqCategory,
        "seq_category_set_id",
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "protocol_id"
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


class SeqDistance(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqDistance)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "sample_id"
    )
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "protocol_id"
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
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "protocol_id"
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
