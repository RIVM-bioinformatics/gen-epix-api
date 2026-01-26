from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.abac.rights import (
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.casedb.domain.model.case.reference_data import (
    CaseType,
    CaseTypeCol,
    CaseTypeDim,
    Col,
    Dim,
    GeneticDistanceProtocol,
    TreeAlgorithm,
)
from gen_epix.casedb.domain.model.ontology import EtiologicalAgent, Etiology
from gen_epix.fastapp.domain import Entity
from gen_epix.util import copy_model_field


class CompleteCaseType(CaseType):
    """
    A complete case type with all its related entities, to avoid multiple queries
    and allow efficient access. The complete case type is unique for each
    (id, user_id) whereby id is the inherited case type id.
    """

    NAME: ClassVar = "CompleteCaseType"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_case_types",
        persistable=False,
    )
    user_id: UUID | None = Field(
        description="The ID of the user for whom the complete case type is retrieved."
    )
    etiologies: dict[UUID, Etiology] = Field(
        description="The etiologies used by the case type"
    )
    etiological_agents: dict[UUID, EtiologicalAgent] = Field(
        description="The etiological agents used by the case type"
    )
    dims: dict[UUID, Dim] = Field(description="The dimensions used by the case type")
    cols: dict[UUID, Col] = Field(description="The columns used by the case type")
    case_type_dims: dict[UUID, CaseTypeDim] = Field(
        description="The case type dimensions"
    )
    case_type_cols: dict[UUID, CaseTypeCol] = Field(
        description="The case type columns for the case type"
    )
    ordered_case_type_dim_ids: list[UUID] = Field(
        default_factory=list,
        description="The case type dimensions ordered by their (occurrence, rank, code). Calculated during model validation.",
    )
    ordered_case_type_col_ids: list[UUID] = Field(
        default_factory=list,
        description="The case type columns ordered by their (ordered_case_type_dim, rank, code). Calculated during model validation.",
    )
    ordered_case_type_col_ids_by_dim: dict[UUID, list[UUID]] = Field(
        default_factory=dict,
        description="The case type columns per case type dimension, ordered by (rank, code). Calculated during model validation.",
    )
    genetic_distance_protocols: dict[UUID, GeneticDistanceProtocol] = Field(
        description="The genetic distance protocols used by the case type"
    )
    tree_algorithms: dict[enum.TreeAlgorithmType, TreeAlgorithm] = Field(
        description="The tree algorithms used by the case type"
    )
    case_type_access_abacs: dict[UUID, CaseTypeAccessAbac] = Field(
        description="The case type access ABAC object by data collection ID"
    )
    case_type_share_abacs: dict[UUID, CaseTypeShareAbac] = Field(
        description="The case type share ABAC object by data collection ID"
    )
    case_date_case_type_dim_id: UUID | None = Field(
        description="The case type dimension ID to use for time-based statistics unless otherwise specified"
    )
    case_date_col_type_map: dict[enum.ColType, UUID] = Field(
        default_factory=dict,
        description="The mapping of column types, restricted to time-related column types, to column IDs for the case date column of the case type. Calculated during model validation.",
    )
    create_max_n_cases: int = copy_model_field(CaseType, "create_max_n_cases")
    read_max_n_cases: int = copy_model_field(CaseType, "read_max_n_cases")
    read_max_tree_size: int = copy_model_field(CaseType, "read_max_tree_size")
    update_max_n_cases: int = copy_model_field(CaseType, "update_max_n_cases")
    delete_max_n_cases: int = copy_model_field(CaseType, "delete_max_n_cases")

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if (
            self.case_date_case_type_dim_id is not None
            and self.case_date_case_type_dim_id not in self.case_type_dims
        ):
            raise ValueError(
                "stats_time_case_type_dim_id must refer to a valid CaseTypeDim"
            )
        # Calculate ordered_case_type_dim_ids
        self.ordered_case_type_dim_ids = [  # type: ignore[assignment]
            y.id
            for y in sorted(
                self.case_type_dims.values(),
                key=lambda x: (x.occurrence, x.rank, x.code),
            )
        ]
        # Calculate ordered_case_type_col_ids
        case_type_dim_order_map = {
            x: i for i, x in enumerate(self.ordered_case_type_dim_ids)
        }
        self.ordered_case_type_col_ids = [  # type: ignore[assignment]
            y.id
            for y in sorted(
                self.case_type_cols.values(),
                key=lambda x: (
                    case_type_dim_order_map[x.case_type_dim_id],
                    x.rank,
                    x.code,
                ),
            )
        ]
        # Calculate ordered_case_type_col_ids_by_dim
        ordered_case_type_col_ids_by_dim: dict[UUID, list[UUID]] = {}
        for case_type_dim_id in self.case_type_dims.keys():
            dim_case_type_cols = [
                x
                for x in self.case_type_cols.values()
                if x.case_type_dim_id == case_type_dim_id
            ]
            ordered_dim_case_type_cols: list[UUID] = [  # type: ignore[assignment]
                y.id
                for y in sorted(
                    dim_case_type_cols,
                    key=lambda x: (x.rank, x.code),
                )
            ]
            ordered_case_type_col_ids_by_dim[case_type_dim_id] = (
                ordered_dim_case_type_cols
            )
        self.ordered_case_type_col_ids_by_dim = ordered_case_type_col_ids_by_dim
        # Calculate case_date_col_type_map
        self.case_date_col_type_map: dict[enum.ColType, UUID] = {}
        if self.case_date_case_type_dim_id is not None:
            case_type_col_ids = self.ordered_case_type_col_ids_by_dim[
                self.case_date_case_type_dim_id
            ]
            time_col_types = enum.ColTypeSet.TIME.value
            for case_type_col_id in case_type_col_ids:
                case_type_col = self.case_type_cols[case_type_col_id]
                col = self.cols[case_type_col.col_id]
                if col.col_type not in time_col_types:
                    continue
                if col.col_type in self.case_date_col_type_map:
                    raise ValueError(
                        f"Multiple case date columns found for col_type {col.col_type}"
                    )
                self.case_date_col_type_map[col.col_type] = case_type_col_id
        return self
