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
    """Request deletion of all persisted casedb reference data.

    `UserAccessCasePolicy` and `UserShareCasePolicy` are not reference data: admins
    create them, and the reference dataset contains no rows for them, so a refdata
    apply cannot restore them. They are therefore kept, together with the models
    they link to within casedb (`CaseTypeSet`, `CaseTypeSetCategory`, `ColSet`), as
    deleting those would violate the policies' foreign keys. The refdata apply
    syncs rows by ID, so it updates the kept sets in place. Their members
    (`CaseTypeSetMember`, `ColSetMember`) are deleted and recreated. A set that a
    later dataset no longer contains is not removed by a reset.
    """

    SORTED_REF_DATA_MODEL_CLASSES = [
        model.OrganizationAccessCasePolicy,
        model.OrganizationShareCasePolicy,
        model.ColSetMember,
        model.Col,
        model.Dim,
        model.CaseTypeSetMember,
        model.CaseType,
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
