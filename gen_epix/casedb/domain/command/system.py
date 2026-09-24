"""Define casedb commands for system operations."""

from gen_epix.casedb.domain import model
from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
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
