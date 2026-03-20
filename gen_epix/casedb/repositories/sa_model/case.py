# pylint: disable=too-few-public-methods
from __future__ import (  # Resolves pylint not recognizing Mapped as subscriptable
    annotations,
)

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import orm
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.commondb.repositories.sa_model.organization import IdentifierMixin
from gen_epix.seqdb.domain import enum as seqdb_enum

Base: type = orm.declarative_base(name=enum.ServiceType.CASE.value)


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

    tree_algorithm_class_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "tree_algorithm_class_id"
    )
    seqdb_tree_algorithm_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "seqdb_tree_algorithm_id"
    )
    code: Mapped[enum.TreeAlgorithmType] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "code"
    )
    name: Mapped[str] = create_mapped_column(DOMAIN, model.TreeAlgorithm, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "description"
    )
    is_ultrametric: Mapped[bool] = create_mapped_column(
        DOMAIN, model.TreeAlgorithm, "is_ultrametric"
    )

    tree_algorithm_class: Mapped[TreeAlgorithmClass] = relationship(
        TreeAlgorithmClass, foreign_keys=[tree_algorithm_class_id]
    )
    rank: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.TreeAlgorithmClass, "rank"
    )


class Protocol(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Protocol)

    seqdb_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN,
        model.Protocol,
        "seqdb_protocol_id",
    )
    seqdb_seq_distance_protocol_type: Mapped[
        seqdb_enum.SeqDistanceProtocolType | None
    ] = create_mapped_column(DOMAIN, model.Protocol, "seqdb_seq_distance_protocol_type")
    seqdb_protocol_type: Mapped[seqdb_enum.ProtocolType] = create_mapped_column(
        DOMAIN, model.Protocol, "seqdb_protocol_type"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Protocol, "code")
    name: Mapped[str | None] = create_mapped_column(DOMAIN, model.Protocol, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Protocol, "description"
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
    ref_seq_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Protocol, "ref_seq_id"
    )
    locus_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Protocol, "locus_set_id"
    )
    valid_start_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_start_date"
    )
    valid_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Protocol, "valid_end_date"
    )
    seqdb_max_stored_distance: Mapped[float | None] = create_mapped_column(
        DOMAIN,
        model.Protocol,
        "seqdb_max_stored_distance",
    )
    seqdb_is_integer_distance: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Protocol, "seqdb_is_integer_distance"
    )
    min_scale_unit: Mapped[float] = create_mapped_column(
        DOMAIN, model.Protocol, "min_scale_unit"
    )


class RefDim(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefDim)

    dim_type: Mapped[enum.DimType] = create_mapped_column(
        DOMAIN, model.RefDim, "dim_type"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefDim, "code")
    label: Mapped[str] = create_mapped_column(DOMAIN, model.RefDim, "label")
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.RefDim, "rank")
    col_code_prefix: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.RefDim, "col_code_prefix"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.RefDim, "description"
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.RefDim, "props")


class RefCol(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.RefCol)

    ref_dim_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.RefCol, "ref_dim_id")
    code_suffix: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.RefCol, "code_suffix"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.RefCol, "code")
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.RefCol, "rank")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.RefCol, "label")
    col_type: Mapped[enum.ColType] = create_mapped_column(
        DOMAIN, model.RefCol, "col_type"
    )
    concept_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.RefCol, "concept_set_id"
    )
    region_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.RefCol, "region_set_id"
    )
    protocol_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.RefCol, "protocol_id"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.RefCol, "description"
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.RefCol, "props")

    ref_dim: Mapped[RefDim] = relationship(RefDim, foreign_keys=[ref_dim_id])


class CaseType(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseType)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseType, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseType, "description"
    )
    disease_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CaseType, "disease_id"
    )
    etiological_agent_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CaseType, "etiological_agent_id"
    )
    create_max_n_cases: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseType, "create_max_n_cases"
    )
    read_max_n_cases: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseType, "read_max_n_cases"
    )
    read_max_tree_size: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseType, "read_max_tree_size"
    )
    update_max_n_cases: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseType, "update_max_n_cases"
    )
    delete_max_n_cases: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseType, "delete_max_n_cases"
    )


class CaseTypeSetCategory(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeSetCategory)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeSetCategory, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeSetCategory, "description"
    )
    rank: Mapped[int] = create_mapped_column(DOMAIN, model.CaseTypeSetCategory, "rank")
    purpose: Mapped[enum.CaseTypeSetCategoryPurpose] = create_mapped_column(
        DOMAIN, model.CaseTypeSetCategory, "purpose"
    )


class CaseTypeSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeSet)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeSet, "description"
    )
    case_type_set_category_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeSet, "case_type_set_category_id"
    )
    rank: Mapped[float] = create_mapped_column(DOMAIN, model.CaseTypeSet, "rank")

    case_type_set_category: Mapped[CaseTypeSetCategory] = relationship(
        CaseTypeSetCategory, foreign_keys=[case_type_set_category_id]
    )


class CaseTypeSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeSetMember)

    case_type_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeSetMember, "case_type_set_id"
    )
    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeSetMember, "case_type_id"
    )

    case_type_set: Mapped[CaseTypeSet] = relationship(
        CaseTypeSet, foreign_keys=[case_type_set_id]
    )
    case_type: Mapped[CaseType] = relationship(CaseType, foreign_keys=[case_type_id])


class Dim(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Dim)

    case_type_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Dim, "case_type_id")
    ref_dim_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Dim, "ref_dim_id")
    occurrence: Mapped[int] = create_mapped_column(DOMAIN, model.Dim, "occurrence")
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Dim, "code")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.Dim, "label")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Dim, "description"
    )
    rank: Mapped[int] = create_mapped_column(DOMAIN, model.Dim, "rank")
    is_case_date_dim: Mapped[bool] = create_mapped_column(
        DOMAIN, model.Dim, "is_case_date_dim"
    )

    ref_dim: Mapped[RefDim] = relationship(RefDim, foreign_keys=[ref_dim_id])


class Col(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Col)

    case_type_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Col, "case_type_id")
    dim_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Col, "dim_id")
    ref_col_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Col, "ref_col_id")
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Col, "code")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Col, "description"
    )
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.Col, "rank")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.Col, "label")
    min_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Col, "min_value"
    )
    max_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Col, "max_value"
    )
    min_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Col, "min_datetime"
    )
    max_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Col, "max_datetime"
    )
    min_length: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Col, "min_length"
    )
    max_length: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Col, "max_length"
    )
    pattern: Mapped[str | None] = create_mapped_column(DOMAIN, model.Col, "pattern")
    ncbi_taxid: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Col, "ncbi_taxid"
    )
    genetic_sequence_col_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Col, "genetic_sequence_col_id"
    )
    tree_algorithm_codes: Mapped[list[enum.TreeAlgorithmType] | None] = (
        create_mapped_column(DOMAIN, model.Col, "tree_algorithm_codes")
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.Col, "props")

    case_type: Mapped[CaseType] = relationship(CaseType, foreign_keys=[case_type_id])
    ref_col: Mapped[RefCol] = relationship(RefCol, foreign_keys=[ref_col_id])
    dim: Mapped[Dim] = relationship(Dim, foreign_keys=[dim_id])


class ColSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ColSet)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.ColSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ColSet, "description"
    )


class ColSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.ColSetMember)

    col_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ColSetMember, "col_set_id"
    )
    col_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.ColSetMember, "col_id")

    col_set: Mapped[ColSet] = relationship(ColSet, foreign_keys=[col_set_id])
    col: Mapped[Col] = relationship(Col, foreign_keys=[col_id])


class Case(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Case)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Case, "case_type_id"
    )
    created_in_data_collection_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Case, "created_in_data_collection_id"
    )
    count: Mapped[int | None] = create_mapped_column(DOMAIN, model.Case, "count")
    case_date: Mapped[datetime] = create_mapped_column(DOMAIN, model.Case, "case_date")
    content: Mapped[dict[UUID, str]] = create_mapped_column(
        DOMAIN, model.Case, "content"
    )

    case_type: Mapped[CaseType] = relationship(CaseType, foreign_keys=[case_type_id])
    code: Mapped[str | None] = create_mapped_column(DOMAIN, model.Case, "code")


class CaseIdentifier(Base, IdentifierMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseIdentifier)

    internal_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseIdentifier, "internal_id"
    )
    case: Mapped[Case] = relationship(Case, foreign_keys=[internal_id])


class CaseDataCollectionLink(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseDataCollectionLink)

    case_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseDataCollectionLink, "case_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseDataCollectionLink, "data_collection_id"
    )

    case: Mapped[Case] = relationship(Case, foreign_keys=[case_id])


class CaseSetCategory(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseSetCategory)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseSetCategory, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseSetCategory, "description"
    )


class CaseSetStatus(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseSetStatus)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseSetStatus, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseSetStatus, "description"
    )


class CaseSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseSet)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSet, "case_type_id"
    )
    created_in_data_collection_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CaseSet, "created_in_data_collection_id"
    )
    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseSet, "name")
    description: Mapped[str] = create_mapped_column(
        DOMAIN, model.CaseSet, "description"
    )
    created_at: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.CaseSet, "created_at"
    )
    case_set_category_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSet, "case_set_category_id"
    )
    case_set_status_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSet, "case_set_status_id"
    )

    case_type: Mapped[CaseType] = relationship(CaseType, foreign_keys=[case_type_id])
    case_set_category: Mapped[CaseSetCategory] = relationship(
        CaseSetCategory, foreign_keys=[case_set_category_id]
    )
    case_set_status: Mapped[CaseSetStatus] = relationship(
        CaseSetStatus, foreign_keys=[case_set_status_id]
    )


class CaseSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseSetMember)

    case_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSetMember, "case_set_id"
    )
    case_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.CaseSetMember, "case_id")
    classification: Mapped[enum.CaseClassification] = create_mapped_column(
        DOMAIN, model.CaseSetMember, "classification"
    )

    case_set: Mapped[CaseSet] = relationship(CaseSet, foreign_keys=[case_set_id])
    case: Mapped[Case] = relationship(Case, foreign_keys=[case_id])


class CaseSetDataCollectionLink(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseSetDataCollectionLink)

    case_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSetDataCollectionLink, "case_set_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSetDataCollectionLink, "data_collection_id"
    )

    case_set: Mapped[CaseSet] = relationship(CaseSet, foreign_keys=[case_set_id])
