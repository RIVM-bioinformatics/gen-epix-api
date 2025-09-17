from typing import ClassVar
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.abac.rights import (
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.casedb.domain.model.case.case import (
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
