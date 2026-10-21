"""Define casedb commands for system operations."""

from gen_epix.casedb.domain import model
from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.commondb.domain.command.system import (
    DeleteAllRefDataCommand as CommonDeleteAllRefDataCommand,
)


class DeleteAllOperationalDataCommand(CommonDeleteAllOperationalDataCommand):
    """Represents a request to delete all CASEDB operational data."""

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

    SORTED_REF_DATA_MODEL_CLASSES = [
        model.UserAccessCasePolicy,
        model.UserShareCasePolicy,
        model.OrganizationAccessCasePolicy,
        model.OrganizationShareCasePolicy,
        model.ColSetMember,
        model.ColSet,
        model.Col,
        model.Dim,
        model.CaseTypeSetMember,
        model.CaseTypeSet,
        model.CaseType,
        model.CaseTypeSetCategory,
        model.CaseSetStatus,
        model.CaseSetCategory,
        model.RefCol,
        model.RefDim,
        model.ConceptRelation,
        model.Concept,
        model.ConceptSet,
        model.RegionRelation,
        model.RegionSetShape,
        model.Region,
        model.RegionSet,
        model.TreeAlgorithm,
        model.GeneticDistanceProtocol,
        model.TreeAlgorithmClass,
        model.Etiology,
        model.EtiologicalAgent,
        model.Disease,
    ]
