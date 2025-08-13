# pylint: disable=too-few-public-methods

from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.common.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.base import (
    AlignmentMixin,
    CodeMixin,
    ProtocolMixin,
    QualityMixin,
    SeqMixin,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.SEQ.value)

# TODO: add SA relationship calls


class AlignmentProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.AlignmentProtocol)

    is_multiple: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AlignmentProtocol, "is_multiple"
    )


class AssemblyProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.AssemblyProtocol)

    has_manual_curation: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AssemblyProtocol, "has_manual_curation"
    )


class AstProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.AstProtocol)

    antimicrobial_names: Mapped[list[str]] = create_mapped_column(
        DOMAIN, model.AstProtocol, "antimicrobial_names"
    )
    is_predicted: Mapped[bool] = create_mapped_column(
        DOMAIN, model.AstProtocol, "is_predicted"
    )


class RefSnp(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RefSnp)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "code")
    ref_seq_id: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "ref_seq_id")
    position: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "position")
    nucleotide: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnp, "nucleotide")


class SnpDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.SnpDetectionProtocol)


class KmerDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.KmerDetectionProtocol)


class RefSnpSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RefSnpSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnpSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.RefSnpSet, "name")


class RefSnpSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RefSnpSetMember)

    ref_snp_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RefSnpSetMember, "ref_snp_set_id"
    )
    ref_snp_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RefSnpSetMember, "ref_snp_id"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.RefSnpSetMember, "index")


class LibraryPrepProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.LibraryPrepProtocol)


class Locus(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Locus)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Locus, "code")
    gene_code: Mapped[str] = create_mapped_column(DOMAIN, model.Locus, "gene_code")
    product_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.Locus, "product_name"
    )


class LocusDetectionProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.LocusDetectionProtocol)


class LocusSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.LocusSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.LocusSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.LocusSet, "name")
    n_loci: Mapped[int] = create_mapped_column(DOMAIN, model.LocusSet, "n_loci")
    locus_ids: Mapped[list[UUID]] = create_mapped_column(
        DOMAIN, model.LocusSet, "locus_ids"
    )


class LocusSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.LocusSetMember)

    locus_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusSetMember, "locus_set_id"
    )
    locus_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocusSetMember, "locus_id"
    )
    index: Mapped[int] = create_mapped_column(DOMAIN, model.LocusSetMember, "index")


class RefAllele(Base, RowMetadataMixin, SeqMixin):
    __tablename__, __table_args__ = create_table_args(model.RefAllele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.RefAllele, "locus_id")
    index: Mapped[int] = create_mapped_column(DOMAIN, model.RefAllele, "index")


class PcrProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.PcrProtocol)

    target_names: Mapped[list[str]] = create_mapped_column(
        DOMAIN, model.PcrProtocol, "target_names"
    )


class SeqCategorySet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqCategorySet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "name")


class SeqCategory(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqCategory)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SeqCategory, "name")
    seq_category_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqCategory, "seq_category_set_id"
    )


class SeqClassificationProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqClassificationProtocol)

    is_taxonomic: Mapped[bool] = create_mapped_column(
        DOMAIN, model.SeqClassificationProtocol, "is_taxonomic"
    )


class SeqDistanceProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqDistanceProtocol)

    max_stored_distance: Mapped[float] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "max_stored_distance"
    )
    min_scale_unit: Mapped[float] = create_mapped_column(
        DOMAIN, model.SeqDistanceProtocol, "min_scale_unit"
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


class SubtypingScheme(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SubtypingScheme)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.SubtypingScheme, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.SubtypingScheme, "name")
    description: Mapped[str] = create_mapped_column(
        DOMAIN, model.SubtypingScheme, "description"
    )


class Taxon(Base, RowMetadataMixin):
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
    subtyping_scheme_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Taxon, "subtyping_scheme_id"
    )
    ncbi_ancestor_taxids: Mapped[list[int]] = create_mapped_column(
        DOMAIN, model.Taxon, "ncbi_ancestor_taxids"
    )
    ancestor_taxon_ids: Mapped[list[UUID]] = create_mapped_column(
        DOMAIN, model.Taxon, "ancestor_taxon_ids"
    )


class TaxonLocusLink(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.TaxonLocusLink)

    taxon_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonLocusLink, "taxon_id"
    )
    locus_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonLocusLink, "locus_id"
    )


class TaxonomyProtocol(Base, RowMetadataMixin, ProtocolMixin):
    __tablename__, __table_args__ = create_table_args(model.TaxonomyProtocol)


class TaxonSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.TaxonSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.TaxonSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.TaxonSet, "name")


class TaxonSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.TaxonSetMember)

    taxon_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonSetMember, "taxon_set_id"
    )
    taxon_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TaxonSetMember, "taxon_id"
    )


class TreeAlgorithm(Base, RowMetadataMixin):
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


class Allele(Base, RowMetadataMixin, SeqMixin, QualityMixin):
    __tablename__, __table_args__ = create_table_args(model.Allele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Allele, "locus_id")


class AlleleAlignment(Base, RowMetadataMixin, AlignmentMixin, QualityMixin):
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
    __tablename__, __table_args__ = create_table_args(model.AlleleProfile)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.AlleleProfile, "seq_id")
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
    allele_profile_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.AlleleProfile, "allele_profile_hash_sha256"
    )


class SnpProfile(Base, RowMetadataMixin, QualityMixin):
    __tablename__, __table_args__ = create_table_args(model.SnpProfile)

    ref_seq_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "ref_seq_id"
    )
    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.SnpProfile, "seq_id")
    snp_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_detection_protocol_id"
    )
    snp_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile"
    )
    snp_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile_format"
    )
    snp_profile_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.SnpProfile, "snp_profile_hash_sha256"
    )


class KmerProfile(Base, RowMetadataMixin, QualityMixin):
    __tablename__, __table_args__ = create_table_args(model.KmerProfile)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.KmerProfile, "seq_id")
    kmer_detection_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_detection_protocol_id"
    )
    kmer_profile: Mapped[str] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile"
    )
    kmer_profile_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile_format"
    )
    kmer_profile_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.KmerProfile, "kmer_profile_hash_sha256"
    )


class AstMeasurement(Base, RowMetadataMixin):
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
    __tablename__, __table_args__ = create_table_args(model.AstPrediction)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.AstPrediction, "seq_id")
    ast_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_protocol_id"
    )
    ast_result: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result"
    )
    ast_result_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.AstPrediction, "ast_result_format"
    )


class PcrMeasurement(Base, RowMetadataMixin):
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


class ReadSet(Base, RowMetadataMixin, CodeMixin, QualityMixin):
    __tablename__, __table_args__ = create_table_args(model.ReadSet)

    uri: Mapped[str] = create_mapped_column(DOMAIN, model.ReadSet, "uri")
    uri2: Mapped[str] = create_mapped_column(DOMAIN, model.ReadSet, "uri2")
    reads_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.ReadSet, "reads_hash_sha256"
    )
    reads2_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.ReadSet, "reads_hash_sha256"
    )
    library_prep_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSet, "library_prep_protocol_id"
    )
    sequencing_run_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.ReadSet, "sequencing_run_code"
    )


class RawSeq(Base, RowMetadataMixin, SeqMixin):
    __tablename__, __table_args__ = create_table_args(model.RawSeq)


class RefSeq(Base, RowMetadataMixin, SeqMixin):
    __tablename__, __table_args__ = create_table_args(model.RefSeq)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "name")
    description: Mapped[str] = create_mapped_column(DOMAIN, model.RefSeq, "description")
    taxon_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.RefSeq, "taxon_id")
    genbank_accession_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.RefSeq, "genbank_accession_code"
    )


class Sample(Base, RowMetadataMixin, CodeMixin):
    __tablename__, __table_args__ = create_table_args(model.Sample)

    props: Mapped[dict[str, str]] = create_mapped_column(DOMAIN, model.Sample, "props")


class Seq(Base, RowMetadataMixin, CodeMixin, QualityMixin):
    __tablename__, __table_args__ = create_table_args(model.Seq)

    sample_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "sample_id")
    read_set_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "read_set_id")
    read_set2_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "read_set2_id")
    assembly_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Seq, "assembly_protocol_id"
    )
    raw_seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "raw_seq_id")


class SeqAlignment(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqAlignment)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.SeqAlignment, "seq_id")
    alignment_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqAlignment, "alignment_protocol_id"
    )
    contig_alignments: Mapped[list[model.ContigAlignment]] = create_mapped_column(
        DOMAIN, model.SeqAlignment, "contig_alignments"
    )


class SeqClassification(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqClassification)

    seq_id: Mapped[UUID] = create_mapped_column(
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
    classification_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.SeqClassification, "classification_hash_sha256"
    )


class SeqDistance(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqDistance)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.SeqDistance, "seq_id")
    seq_distance_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "seq_distance_protocol_id"
    )
    allele_profile_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "allele_profile_id"
    )
    snp_profile_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "snp_profile_id"
    )
    kmer_profile_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "kmer_profile_id"
    )
    distance_format: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqDistance, "distance_format"
    )
    distances: Mapped[str] = create_mapped_column(
        DOMAIN, model.SeqDistance, "distances"
    )


class SeqTaxonomy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SeqTaxonomy)

    seq_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.SeqTaxonomy, "seq_id")
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
    taxonomy_hash_sha256: Mapped[bytes] = create_mapped_column(
        DOMAIN, model.SeqTaxonomy, "taxonomy_hash_sha256"
    )
