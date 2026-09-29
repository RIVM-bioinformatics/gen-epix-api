"""Define casedb commands for system operations."""

from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.seqdb.domain import model


class DeleteAllOperationalDataCommand(CommonDeleteAllOperationalDataCommand):
    SORTED_OPERATIONAL_DATA_MODEL_CLASSES = [
        model.SeqDistance,
        model.SeqProfileIdentifier,
        model.SeqProfile,
        model.SeqTaxonomy,
        model.SeqClassification,
        model.AstPrediction,
        model.SeqIdentifier,
        model.Seq,
        model.ReadSetIdentifier,
        model.ReadSet,
        model.PcrMeasurement,
        model.AstMeasurement,
        model.SampleIdentifier,
        model.SampleDataCollectionLink,
        model.Sample,
        model.File,
    ]
