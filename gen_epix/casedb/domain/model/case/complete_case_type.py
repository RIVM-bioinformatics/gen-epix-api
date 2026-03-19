from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.abac.rights import (
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.casedb.domain.model.case.ref_data import (
    CaseType,
    Col,
    Dim,
    Protocol,
    RefCol,
    RefDim,
    TreeAlgorithm,
)
from gen_epix.casedb.domain.model.ontology import EtiologicalAgent, Etiology
from gen_epix.fastapp.domain import Entity
from gen_epix.util import copy_model_field


class CompleteCaseType(CaseType):
    """
    A complete CaseType with all its related entities, to avoid multiple queries
    and allow efficient access. The complete CaseType is unique for each
    (id, user_id) whereby ID is the inherited CaseType ID.
    """

    NAME: ClassVar = "CompleteCaseType"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_case_types",
        persistable=False,
    )
    user_id: UUID | None = Field(
        description="The ID of the user for whom the complete CaseType is retrieved."
    )
    etiologies: dict[UUID, Etiology] = Field(
        description="The etiologies used by the CaseType"
    )
    etiological_agents: dict[UUID, EtiologicalAgent] = Field(
        description="The etiological agents used by the CaseType"
    )
    ref_dims: dict[UUID, RefDim] = Field(
        description="The reference dimensions used by the CaseType"
    )
    ref_cols: dict[UUID, RefCol] = Field(
        description="The reference columns used by the CaseType"
    )
    dims: dict[UUID, Dim] = Field(description="The Dims for the CaseType")
    cols: dict[UUID, Col] = Field(description="The Cols for the CaseType")
    ordered_dim_ids: list[UUID] = Field(
        default_factory=list,
        description="The Dims ordered by their (occurrence, rank, code). Calculated during model validation.",
    )
    ordered_col_ids: list[UUID] = Field(
        default_factory=list,
        description="The Cols ordered by their (ordered_dim, rank, code). Calculated during model validation.",
    )
    ordered_col_ids_by_dim: dict[UUID, list[UUID]] = Field(
        default_factory=dict,
        description="The Cols per Dim, ordered by (rank, code). Calculated during model validation.",
    )
    protocols: dict[UUID, Protocol] = Field(
        description="protocols used by the CaseType"
    )
    tree_algorithms: dict[enum.TreeAlgorithmType, TreeAlgorithm] = Field(
        description="The tree algorithms used by the CaseType"
    )
    case_type_access_abacs: dict[UUID, CaseTypeAccessAbac] = Field(
        description="The CaseTypeAccessAbac objects by data collection ID"
    )
    case_type_share_abacs: dict[UUID, CaseTypeShareAbac] = Field(
        description="The CaseTypeShareAbac objects by data collection ID"
    )
    case_date_dim_id: UUID | None = Field(
        description="The Dim ID to use for time-based statistics unless otherwise specified"
    )
    case_date_col_type_map: dict[enum.ColType, UUID] = Field(
        default_factory=dict,
        description="The mapping of column types, restricted to time-related column types, to column IDs for the case date column of the CaseType. Calculated during model validation.",
    )
    create_max_n_cases: int = copy_model_field(CaseType, "create_max_n_cases")
    read_max_n_cases: int = copy_model_field(CaseType, "read_max_n_cases")
    read_max_tree_size: int = copy_model_field(CaseType, "read_max_tree_size")
    update_max_n_cases: int = copy_model_field(CaseType, "update_max_n_cases")
    delete_max_n_cases: int = copy_model_field(CaseType, "delete_max_n_cases")

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.case_date_dim_id is not None and self.case_date_dim_id not in self.dims:
            raise ValueError("stats_time_dim_id must refer to a valid Dim")
        # Calculate ordered_dim_ids
        self.ordered_dim_ids = [  # type: ignore[assignment]
            y.id
            for y in sorted(
                self.dims.values(),
                key=lambda x: (x.occurrence, x.rank, x.code),
            )
        ]
        # Calculate ordered_col_ids
        dim_order_map = {x: i for i, x in enumerate(self.ordered_dim_ids)}
        self.ordered_col_ids = [  # type: ignore[assignment]
            y.id
            for y in sorted(
                self.cols.values(),
                key=lambda x: (
                    dim_order_map[x.dim_id],
                    x.rank,
                    x.code,
                ),
            )
        ]
        # Calculate ordered_col_ids_by_dim
        ordered_col_ids_by_dim: dict[UUID, list[UUID]] = {}
        for dim_id in self.dims.keys():
            dim_cols = [x for x in self.cols.values() if x.dim_id == dim_id]
            ordered_dim_cols: list[UUID] = [  # type: ignore[assignment]
                y.id
                for y in sorted(
                    dim_cols,
                    key=lambda x: (x.rank, x.code),
                )
            ]
            ordered_col_ids_by_dim[dim_id] = ordered_dim_cols
        self.ordered_col_ids_by_dim = ordered_col_ids_by_dim
        # Calculate case_date_col_type_map
        self.case_date_col_type_map: dict[enum.ColType, UUID] = {}
        if self.case_date_dim_id is not None:
            col_ids = self.ordered_col_ids_by_dim[self.case_date_dim_id]
            time_col_types = enum.ColTypeSet.TIME.value
            for col_id in col_ids:
                col = self.cols[col_id]
                ref_col = self.ref_cols[col.ref_col_id]
                if ref_col.col_type not in time_col_types:
                    continue
                if ref_col.col_type in self.case_date_col_type_map:
                    raise ValueError(
                        f"Multiple case date columns found for col_type {ref_col.col_type}"
                    )
                self.case_date_col_type_map[ref_col.col_type] = col_id
        return self
