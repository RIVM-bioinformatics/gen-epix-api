"""Define casedb commands for system operations."""

from typing import ClassVar

from gen_epix.casedb.domain import model
from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.commondb.domain.command.system import (
    DeleteAllRefDataCommand as CommonDeleteAllRefDataCommand,
)


class DeleteAllOperationalDataCommand(CommonDeleteAllOperationalDataCommand):
    SORTED_OPERATIONAL_DATA_MODEL_CLASSES = [
        model.CaseSetDataCollectionLink,
        model.CaseDataCollectionLink,
        model.CaseSetMember,
        model.CaseSet,
        model.CaseIdentifier,
        model.Case,
    ]


class DeleteAllRefDataCommand(CommonDeleteAllRefDataCommand):
    """Request deletion of all persisted casedb reference data."""

    REF_DATA_SERVICE_TYPE_VALUES: ClassVar[frozenset[str]] = frozenset(
        {"CASE", "GEO", "ONTOLOGY", "SEQDB"}
    )
    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.Model]]] = [
        model.ColSetMember,
        model.Col,
        model.CaseTypeSetMember,
        model.RegionRelation,
        model.Dim,
        model.ConceptRelation,
        model.CaseTypeSet,
        model.RefCol,
        model.TreeAlgorithm,
        model.RegionSetShape,
        model.Region,
        model.CaseType,
        model.Etiology,
        model.Concept,
        model.CaseSetStatus,
        model.CaseSetCategory,
        model.ColSet,
        model.CaseTypeSetCategory,
        model.RefDim,
        model.GeneticDistanceProtocol,
        model.TreeAlgorithmClass,
        model.RegionSet,
        model.EtiologicalAgent,
        model.Disease,
        model.ConceptSet,
    ]
