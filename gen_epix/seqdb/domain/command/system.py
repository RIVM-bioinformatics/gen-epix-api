"""Define seqdb commands for system operations."""

from typing import ClassVar

from gen_epix.commondb.domain.command.system import (
    DeleteAllOperationalDataCommand as CommonDeleteAllOperationalDataCommand,
)
from gen_epix.commondb.domain.command.system import (
    DeleteAllRefDataCommand as CommonDeleteAllRefDataCommand,
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


class DeleteAllRefDataCommand(CommonDeleteAllRefDataCommand):
    """Request deletion of all persisted seqdb reference data."""

    REF_DATA_SERVICE_TYPE_VALUES: ClassVar[frozenset[str]] = frozenset({"FILE", "SEQ"})
    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.Model]]] = [
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
