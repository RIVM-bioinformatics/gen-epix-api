# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from datetime import datetime
from typing import Any, Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.common.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.CASE.value)


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


class TreeAlgorithm(Base, RowMetadataMixin):
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
    __tablename__, __table_args__ = create_table_args(model.GeneticDistanceProtocol)

    seqdb_seq_distance_protocol_id: Mapped[UUID] = create_mapped_column(
        DOMAIN,
        model.GeneticDistanceProtocol,
        "seqdb_seq_distance_protocol_id",
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
    min_scale_unit: Mapped[float] = create_mapped_column(
        DOMAIN, model.GeneticDistanceProtocol, "min_scale_unit"
    )


class Dim(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Dim)

    dim_type: Mapped[enum.DimType] = create_mapped_column(DOMAIN, model.Dim, "dim_type")
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Dim, "code")
    label: Mapped[str] = create_mapped_column(DOMAIN, model.Dim, "label")
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.Dim, "rank")
    col_code_prefix: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Dim, "col_code_prefix"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Dim, "description"
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.Dim, "props")


class Col(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Col)

    dim_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Col, "dim_id")
    code_suffix: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Col, "code_suffix"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Col, "code")
    rank_in_dim: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Col, "rank_in_dim"
    )
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.Col, "label")
    col_type: Mapped[enum.ColType] = create_mapped_column(DOMAIN, model.Col, "col_type")
    concept_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Col, "concept_set_id"
    )
    region_set_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Col, "region_set_id"
    )
    genetic_distance_protocol_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Col, "genetic_distance_protocol_id"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Col, "description"
    )
    props: Mapped[dict[str, Any]] = create_mapped_column(DOMAIN, model.Col, "props")

    dim: Mapped[Dim] = relationship(Dim, foreign_keys=[dim_id])


class CaseType(Base, RowMetadataMixin):
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


class CaseTypeSetCategory(Base, RowMetadataMixin):
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
    __tablename__, __table_args__ = create_table_args(model.CaseTypeCol)

    case_type_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "case_type_id"
    )
    col_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.CaseTypeCol, "col_id")
    occurrence: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "occurrence"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeCol, "code")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "description"
    )
    rank: Mapped[int | None] = create_mapped_column(DOMAIN, model.CaseTypeCol, "rank")
    label: Mapped[str | None] = create_mapped_column(DOMAIN, model.CaseTypeCol, "label")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeCol, "description"
    )
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
    col: Mapped[Col] = relationship(Col, foreign_keys=[col_id])


class CaseTypeColSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CaseTypeColSet)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseTypeColSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseTypeColSet, "description"
    )


class CaseTypeColSetMember(Base, RowMetadataMixin):
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


class Case(Base, RowMetadataMixin):
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


class CaseDataCollectionLink(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CaseDataCollectionLink)

    case_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseDataCollectionLink, "case_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseDataCollectionLink, "data_collection_id"
    )

    case: Mapped[Case] = relationship(Case, foreign_keys=[case_id])


class CaseSetCategory(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CaseSetCategory)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseSetCategory, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseSetCategory, "description"
    )


class CaseSetStatus(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CaseSetStatus)

    name: Mapped[str] = create_mapped_column(DOMAIN, model.CaseSetStatus, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CaseSetStatus, "description"
    )


class CaseSet(Base, RowMetadataMixin):
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
    __tablename__, __table_args__ = create_table_args(model.CaseSetDataCollectionLink)

    case_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSetDataCollectionLink, "case_set_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CaseSetDataCollectionLink, "data_collection_id"
    )

    case_set: Mapped[CaseSet] = relationship(CaseSet, foreign_keys=[case_set_id])
