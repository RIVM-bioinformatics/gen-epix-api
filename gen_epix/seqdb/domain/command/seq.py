# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.seqdb.domain import enum, model

# Non-CRUD commands


class UploadSamplesCommand(Command, UploadBatchCommandMixin):
    """
    Upload a batch of samples along with their associated data. The data are uploaded
    as a single atomic unit of work, so that either all data are successfully
    uploaded or none are.

    The upload process consists of the following steps:
    1) Check if the user has the rights to upload the data in question.
    2) Verify the validity of the sample data. The verification does not fail fast
       but rather proceeds with the remaining data and checks to the extent possible,
       so that all errors can be reported back to the caller instead of just the
       first encountered one.
    3) Upsert (create and/or update) the sample data.

    The return value contains the results of the upload
    operation, whether successful or otherwise, and with details for each sample and
    associated data item.
    """

    BATCH_FOR_UPLOAD_CLASS: ClassVar = model.SampleBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "sample_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = model.SampleBatchUploadResult

    sample_batch: model.SampleBatchForUpload = Field(
        description="Samples to upload, along with any associated data.",
    )


class GenerateMultipleAlignmentCommand(Command):
    pass


class GeneratePhylogeneticTreeCommand(Command):
    pass


class RetrieveMultipleAlignmentCommand(Command):
    pass


class RetrievePhylogeneticTreeCommand(Command):

    seq_distance_protocol_id: UUID = Field(
        description="The ID of the sequence distance protocol to use for generating the distances"
    )
    tree_algorithm: enum.TreeAlgorithm = Field(
        description="The tree algorithm to use for generating the phylogenetic tree"
    )
    profile_ids: list[UUID] = Field(
        description="List of profile IDs to calculate the phylogenetic tree for"
    )
    leaf_names: list[str] | None = Field(
        default=None,
        description="Optional list of leaf names corresponding to the profile IDs",
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.leaf_names is not None and len(self.leaf_names) != len(
            self.profile_ids
        ):
            raise ValueError(
                "leaf_names must be None or have the same length as profile_ids"
            )
        return self


class RetrieveSamplesCommand(Command):

    sample_ids: list[UUID]


class RetrieveSeqFastaCommand(Command):
    """
    Retrieve the sequences for the given sequence IDs in FASTA format
    as an iterable that yields one contig at a time.
    """

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )
    wrap: int | None = Field(
        default=80,
        description="Number of characters to wrap the sequence lines.",
    )


class GetSimilarProfilesCommand(Command):
    seq_distance_protocol_id: UUID = Field(
        description="ID of the sequence distance protocol to use for similarity search.",
    )
    profile_ids: list[UUID] = Field(
        description="List of profile IDs to find similar profiles for.",
    )
    max_distance: float = Field(
        description="Maximum distance threshold for considering profiles as similar.",
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
