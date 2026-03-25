# pylint: disable=too-few-public-methods
from datetime import datetime
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, relationship

from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.seq.base import (
    SeqMixin,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SEQ.value)


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
    valid_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_start_datetime"
    )
    valid_end_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_end_datetime"
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


class ProtocolSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ProtocolSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.ProtocolSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.ProtocolSet, "name")


class ProtocolSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ProtocolSetMember)

    protocol_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProtocolSetMember, "protocol_set_id"
    )
    protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProtocolSetMember, "protocol_id"
    )

    protocol_set: Mapped[ProtocolSet] = relationship(
        "ProtocolSet",
        foreign_keys=[protocol_set_id],
    )
    protocol: Mapped[Protocol] = relationship(
        "Protocol",
        foreign_keys=[protocol_id],
    )


class Allele(Base, RowMetadataMixin, SeqMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Allele)

    locus_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Allele, "locus_id")


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

    taxon_set: Mapped[TaxonSet] = relationship(
        "TaxonSet",
        foreign_keys=[taxon_set_id],
    )
    taxon: Mapped[Taxon] = relationship(
        "Taxon",
        foreign_keys=[taxon_id],
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

    tree_algorithm_class: Mapped[TreeAlgorithmClass] = relationship(
        "TreeAlgorithmClass",
        foreign_keys=[tree_algorithm_class_id],
    )
