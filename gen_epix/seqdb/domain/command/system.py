"""Define seqdb commands for system operations."""

from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.commondb.domain.command.system import (
    DeleteAllRefDataCommand as CommonDeleteAllRefDataCommand,
)
from gen_epix.seqdb.domain import model


class DeleteAllOperationalDataCommand(CommonDeleteAllOperationalDataCommand):
    """Represents a request to delete all SeqDB operational data."""

    SORTED_OPERATIONAL_DATA_MODEL_CLASSES = [
        model.UploadJob,  # No links; jobs of a reset application are obsolete
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
    # Seq rows are large (the sequence itself), so a batch of them is kept small
    BATCH_SIZE_BY_MODEL = {model.Seq: 100}


class DeleteAllRefDataCommand(CommonDeleteAllRefDataCommand):
    """Request deletion of all persisted seqdb reference data."""

    SORTED_REF_DATA_MODEL_CLASSES = [
        model.ProtocolSetMember,
        model.Protocol,
        model.SeqCategory,
        model.TreeAlgorithm,
        model.Allele,
        model.RefAllele,
        model.LocusCodeMap,
        model.LocusSet,
        model.TaxonSetMember,
        model.RefSeq,
        model.ProtocolSet,
        model.SeqCategorySet,
        model.TreeAlgorithmClass,
        model.Locus,
        model.TaxonSet,
        model.Taxon,
    ]
