from uuid import UUID

from sqlalchemy.orm import Mapped, relationship

from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.commondb.repositories.sa_model.organization import IdentifierMixin
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.seq.base import (
    CodeMixin,
    ContentMixin,
    QualityMixin,
)
from gen_epix.seqdb.repositories.sa_model.seq.ref_data import (
    Base,
    Protocol,
    SeqCategory,
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class ReadSetIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ReadSetIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ReadSetIdentifier, "internal_id"
    )
    read_set: Mapped[ReadSet] = relationship(ReadSet, foreign_keys=[internal_id])


class Seq(Base, RowMetadataMixin, CodeMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Seq)

    sample_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Seq, "sample_id", index=True)
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    read_set: Mapped[ReadSet | None] = relationship(
        "ReadSet", foreign_keys=[read_set_id]
    )
    read_set2: Mapped[ReadSet | None] = relationship(
        "ReadSet", foreign_keys=[read_set2_id]
    )
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class SeqIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqIdentifier, "internal_id"
    )
    seq: Mapped[Seq] = relationship(Seq, foreign_keys=[internal_id])


class AstMeasurement(
    Base, RowMetadataMixin, ContentMixin[enum.AstResultFormat], QualityMixin
):
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class AstPrediction(
    Base, RowMetadataMixin, ContentMixin[enum.AstResultFormat], QualityMixin
):
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    seq: Mapped[Seq | None] = relationship("Seq", foreign_keys=[seq_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class PcrMeasurement(
    Base, RowMetadataMixin, ContentMixin[enum.PcrResultFormat], QualityMixin
):
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class SeqClassification(
    Base, RowMetadataMixin, ContentMixin[enum.SeqClassificationFormat], QualityMixin
):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqClassification)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "sample_id", index=True
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SeqClassification, "seq_id", index=True
    )
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "protocol_id"
    )
    primary_category_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqClassification, "primary_category_id"
    )

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    seq: Mapped[Seq | None] = relationship("Seq", foreign_keys=[seq_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])
    primary_category: Mapped[SeqCategory] = relationship(
        "SeqCategory", foreign_keys=[primary_category_id]
    )


class SeqTaxonomy(
    Base, RowMetadataMixin, ContentMixin[enum.SeqTaxonomyFormat], QualityMixin
):
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

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    seq: Mapped[Seq | None] = relationship("Seq", foreign_keys=[seq_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])
    primary_taxon: Mapped[model.Taxon] = relationship(
        "Taxon", foreign_keys=[primary_taxon_id]
    )


class SeqProfile(Base, RowMetadataMixin, ContentMixin, QualityMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqProfile)

    sample_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqProfile, "sample_id", index=True
    )
    seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SeqProfile, "seq_id"
    )
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqProfile, "protocol_id"
    )
    seq_profile_type: Mapped[enum.SeqProfileType] = create_mapped_column(
        DOMAIN, model.SeqProfile, "seq_profile_type"
    )

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    seq: Mapped[Seq | None] = relationship("Seq", foreign_keys=[seq_id])
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])


class SeqProfileIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SeqProfileIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqProfileIdentifier, "internal_id"
    )
    seq_profile: Mapped[SeqProfile] = relationship(
        SeqProfile, foreign_keys=[internal_id]
    )


class SeqDistance(Base, RowMetadataMixin, ContentMixin[enum.SeqDistanceFormat]):
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
    seq_profile_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SeqDistance, "seq_profile_id"
    )

    sample: Mapped[Sample] = relationship("Sample", foreign_keys=[sample_id])
    seq_profile: Mapped[SeqProfile] = relationship(
        "SeqProfile", foreign_keys=[seq_profile_id]
    )
    protocol: Mapped[Protocol] = relationship("Protocol", foreign_keys=[protocol_id])
