# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.seqdb.domain import enum, model

# Non-CRUD commands


class UpsertCompleteSamplesCommand(Command):
    alleles: list[model.Allele] | None = Field(
        default=None,
        description="List of any not yet existing alleles to create. Any already existing alleles are ignored. None if not set.",
    )
    complete_samples: list[model.CompleteSample] = Field(
        description="List of complete samples to upsert.",
    )


class GenerateMultipleAlignmentCommand(Command):
    pass


class GeneratePhylogeneticTreeCommand(Command):
    pass


class RetrieveCompleteAlleleProfileCommand(Command):
    pass


class RetrieveCompleteContigCommand(Command):
    pass


class RetrieveCompleteSampleCommand(Command):
    pass


class RetrieveCompleteSamplesCommand(Command):

    sample_ids: list[UUID]


class RetrieveCompleteSnpProfileCommand(Command):
    pass


class RetrieveMultipleAlignmentCommand(Command):
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


class RetrieveSeqFastaCommand(Command):

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )
    wrap: int | None = Field(
        default=80,
        description="Number of characters to wrap the sequence lines.",
    )


# CRUD commands


class AlignmentProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlignmentProtocol


class AlleleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Allele


class AlleleAlignmentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlleleAlignment


class AlleleProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AlleleProfile


class AssemblyProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AssemblyProtocol


class AstMeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstMeasurement


class AstPredictionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstPrediction


class AstProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.AstProtocol


class KmerDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.KmerDetectionProtocol


class KmerProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.KmerProfile


class LocusCodeMapCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusCodeMap


class LocusCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Locus


class LocusDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusDetectionProtocol


class LocusProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusProfile


class LocusSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocusSet


class MlvaDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.MlvaDetectionProtocol


class MlvaProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.MlvaProfile


class PcrMeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PcrMeasurement


class PcrProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PcrProtocol


class ReadSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ReadSet


class RefAlleleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefAllele


class RefSeqCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSeq


class RefSnpCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnp


class RefSnpSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnpSet


class RefSnpSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RefSnpSetMember


class SampleCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Sample


class SampleDataCollectionLinkCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SampleDataCollectionLink


class SampleIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SampleIdentifier


class SeqClassificationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqClassification


class SeqClassificationProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqClassificationProtocol


class SeqCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Seq


class SeqAlignmentCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqAlignment


class SeqCategoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqCategory


class SeqCategorySetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqCategorySet


class SeqDistanceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqDistance


class SeqDistanceProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqDistanceProtocol


class SeqTaxonomyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SeqTaxonomy


class SequencingProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SequencingProtocol


class SnpDetectionProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SnpDetectionProtocol


class SnpProfileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SnpProfile


class TaxonomyProtocolCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonomyProtocol


class TaxonCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Taxon


class TaxonSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonSet


class TaxonSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TaxonSetMember


class TreeAlgorithmCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithm


class TreeAlgorithmClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass
