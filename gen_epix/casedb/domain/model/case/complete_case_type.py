from typing import ClassVar
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.abac.rights import (
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.casedb.domain.model.case.non_persistable import CaseTypeDim
from gen_epix.casedb.domain.model.case.persistable import (
    CaseType,
    CaseTypeCol,
    CaseTypeSettings,
    Col,
    Dim,
    GeneticDistanceProtocol,
    TreeAlgorithm,
)
from gen_epix.casedb.domain.model.ontology import EtiologicalAgent, Etiology
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp.domain import Entity


class CompleteCaseType(CaseType):
    NAME: ClassVar = "CompleteCaseType"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_case_types",
        persistable=False,
    )
    etiologies: dict[UUID, Etiology] = Field(
        description="The etiologies used by the case type"
    )
    etiological_agents: dict[UUID, EtiologicalAgent] = Field(
        description="The etiological agents used by the case type"
    )
    dims: dict[UUID, Dim] = Field(description="The dimensions used by the case type")
    cols: dict[UUID, Col] = Field(description="The columns used by the case type")
    case_type_dims: list[CaseTypeDim] = Field(
        description="The ordered list of case type dimensions"
    )
    case_type_cols: dict[UUID, CaseTypeCol] = Field(
        description="The case type columns for the case type"
    )
    case_type_col_order: list[UUID] = Field(
        description="The order of the case type columns outside the context of a dimension"
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
    stats_time_case_type_col_id: UUID | None = copy_model_field(
        CaseTypeSettings, "stats_time_case_type_col_id"
    )
    stats_time_case_type_col: CaseTypeCol | None = copy_model_field(
        CaseTypeSettings, "stats_time_case_type_col"
    )
    stats_geo_case_type_col_id: UUID | None = copy_model_field(
        CaseTypeSettings, "stats_geo_case_type_col_id"
    )
    stats_geo_case_type_col: CaseTypeCol | None = copy_model_field(
        CaseTypeSettings, "stats_geo_case_type_col"
    )
    create_max_n_cases: int = copy_model_field(CaseTypeSettings, "create_max_n_cases")
    read_max_n_cases: int = copy_model_field(CaseTypeSettings, "read_max_n_cases")
    read_max_tree_size: int = copy_model_field(CaseTypeSettings, "read_max_tree_size")
    update_max_n_cases: int = copy_model_field(CaseTypeSettings, "update_max_n_cases")
    delete_max_n_cases: int = copy_model_field(CaseTypeSettings, "delete_max_n_cases")

    stats_time_case_type_col_ids: list[UUID] | None = Field(
        description=(
            "The list of case type column IDs within the stats_time_dim_id. "
            "occurrence None or lowest occurrence in case of more than one, "
            "from highest to lowest resolution (TIME_DAY, WEEK, MONTH, QUARTER, YEAR). "
            "Empty list of stats_time_dim_id is None."
        ),
    )
    stats_geo_case_type_col_ids: list[UUID] | None = Field(
        description=(
            "The list of case type column IDs within the stats_geo_dim_id. "
            "occurrence None or lowest occurrence in case of more than one, "
            "from highest to lowest resolution (using CaseTypeCol.Col.RegionSet.resolution)."
        ),
    )

    @model_validator(mode="after")
    def derive_case_type_col_order(self) -> "CompleteCaseType":
        ordered: list[UUID] = []
        seen: set[UUID] = set()
        for dim in self.case_type_dims:
            for cid in dim.case_type_col_order:
                if cid not in seen:
                    ordered.append(cid)
                    seen.add(cid)
        self.case_type_col_order = ordered
        return self
