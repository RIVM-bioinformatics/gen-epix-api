# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar, Self
from uuid import UUID

from pydantic import model_validator

from gen_epix.common.domain.command import Command, CrudCommand
from gen_epix.seqdb.domain import enum, model

# Non-CRUD commands


class RetrieveCompleteContigCommand(Command):
    pass


class RetrieveCompleteAlleleProfileCommand(Command):
    pass


class RetrieveCompleteSnpProfileCommand(Command):
    pass


class RetrieveCompleteSeqCommand(Command):

    seq_ids: list[UUID]


class RetrieveCompleteSampleCommand(Command):
    pass


class RetrievePhylogeneticTreeCommand(Command):

    seq_distance_protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    seq_ids: list[UUID]
    leaf_names: list[str] | None

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.leaf_names is not None and len(self.leaf_names) != len(self.seq_ids):
            raise ValueError(
                "leaf_codes must be None or have the same length as seq_ids"
            )
        return self


class RetrieveMultipleAlignmentCommand(Command):
    pass


class GenerateMultipleAlignmentCommand(Command):
    pass


class GeneratePhylogeneticTreeCommand(Command):
    pass


# CRUD commands


class TreeAlgorithmClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithm


class LibraryPrepProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LibraryPrepProtocol


class AssemblyProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AssemblyProtocol


class LocusDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusDetectionProtocol


class SnpDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SnpDetectionProtocol


class AlignmentProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlignmentProtocol


class TaxonomyProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonomyProtocol


class SeqClassificationProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqClassificationProtocol


class PcrProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PcrProtocol


class AstProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstProtocol


class SeqDistanceProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqDistanceProtocol


class SeqCategorySetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqCategorySet


class SeqCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqCategory


class SubtypingSchemeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SubtypingScheme


class TaxonCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Taxon


class TaxonSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonSet


class TaxonSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonSetMember


class LocusCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Locus


class LocusSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusSet


class LocusSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusSetMember


class RefAlleleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefAllele


class TaxonLocusLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonLocusLink


class RefSeqCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSeq


class AlleleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Allele


class AlleleAlignmentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlleleAlignment


class SampleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Sample


class ReadSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ReadSet


class RawSeqCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RawSeq


class SeqCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Seq


class SeqAlignmentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqAlignment


class AlleleProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlleleProfile


class RefSnpCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnp


class RefSnpCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnp


class RefSnpSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnpSet


class RefSnpSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnpSetMember


class SeqTaxonomyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqTaxonomy


class PcrMeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PcrMeasurement


class AstMeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstMeasurement


class AstPredictionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstPrediction


class SeqDistanceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqDistance


class SeqClassificationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqClassification


class SnpProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SnpProfile


class KmerProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.KmerProfile


class KmerDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.KmerDetectionProtocol
