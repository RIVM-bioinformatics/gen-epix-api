# pylint: disable=too-few-public-methods
from __future__ import (  # Resolves pylint not recognizing Mapped as subscriptable
    annotations,
)

from datetime import datetime
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


class GeneticDistanceProtocol(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.GeneticDistanceProtocol)

    seqdb_seq_distance_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN,
        model.GeneticDistanceProtocol,
        "seqdb_seq_distance_protocol_id",
    )
    seqdb_seq_distance_protocol_type: Mapped[seqdb_enum.SeqDistanceProtocolType] = (
        create_mapped_column(
            DOMAIN, model.GeneticDistanceProtocol, "seqdb_seq_distance_protocol_type"
        )
    )
    name: Mapped[str] = create_mapped_column(
        DOMAIN, model.GeneticDistanceProtocol, "name"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.GeneticDistanceProtocol, "description"
    )
    seqdb_max_stored_distance: Mapped[float | None] = create_mapped_column(
        DOMAIN,
        model.GeneticDistanceProtocol,
        "seqdb_max_stored_distance",
    )
    seqdb_is_integer_distance: Mapped[bool] = create_mapped_column(
        DOMAIN, model.GeneticDistanceProtocol, "seqdb_is_integer_distance"
    )
    min_scale_unit: Mapped[float] = create_mapped_column(
        DOMAIN, model.GeneticDistanceProtocol, "min_scale_unit"
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
    genetic_distance_protocol_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.RefCol, "genetic_distance_protocol_id"
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


class CaseTypeCol(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeCol)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "case_type_id"
    )
    case_type_dim_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "case_type_dim_id"
    )
    ref_col_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "ref_col_id"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeCol, "code")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "description"
    )
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.CaseTypeCol, "rank")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.CaseTypeCol, "label")
    min_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "min_value"
    )
    max_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "max_value"
    )
    min_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "min_datetime"
    )
    max_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "max_datetime"
    )
    min_length: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "min_length"
    )
    max_length: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "max_length"
    )
    pattern: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "pattern"
    )
    ncbi_taxid: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "ncbi_taxid"
    )
    genetic_sequence_case_type_col_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "genetic_sequence_case_type_col_id"
    )
    tree_algorithm_codes: Mapped[list[enum.TreeAlgorithmType] | None] = (
        create_mapped_column(DOMAIN, model.CaseTypeCol, "tree_algorithm_codes")
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "props"
    )

    case_type: Mapped[CaseType] = relationship(CaseType, foreign_keys=[case_type_id])
    ref_col: Mapped[RefCol] = relationship(RefCol, foreign_keys=[ref_col_id])


class CaseTypeColSet(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeColSet)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeColSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeColSet, "description"
    )


class CaseTypeColSetMember(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.CaseTypeColSetMember)

    case_type_col_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeColSetMember, "case_type_col_set_id"
    )
    case_type_col_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeColSetMember, "case_type_col_id"
    )

    case_type_col_set: Mapped[CaseTypeColSet] = relationship(
        CaseTypeColSet, foreign_keys=[case_type_col_set_id]
    )
    case_type_col: Mapped[CaseTypeCol] = relationship(
        CaseTypeCol, foreign_keys=[case_type_col_id]
    )


class CaseTypeDim(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CaseTypeDim)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeDim, "case_type_id"
    )
    ref_dim_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeDim, "ref_dim_id"
    )
    occurrence: Mapped[int] = create_mapped_column(
        DOMAIN, model.CaseTypeDim, "occurrence"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeDim, "code")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.CaseTypeDim, "label")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeDim, "description"
    )
    rank: Mapped[int] = create_mapped_column(DOMAIN, model.CaseTypeDim, "rank")
    is_case_date_dim: Mapped[bool] = create_mapped_column(
        DOMAIN, model.CaseTypeDim, "is_case_date_dim"
    )

    ref_dim: Mapped[RefDim] = relationship(RefDim, foreign_keys=[ref_dim_id])


class Case(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Case)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Case, "case_type_id"
    )
    subject_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Case, "subject_id"
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
