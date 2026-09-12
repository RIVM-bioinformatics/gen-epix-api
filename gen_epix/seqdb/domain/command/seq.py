"""Define commands for seqdb sequence workflows and managed domain records.

The command types carry input for upload, distance, tree, similarity, and
sample retrieval operations, plus CRUD metadata for seqdb sequence models.
"""

# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.seqdb.domain import enum, model

# Non-CRUD commands


class UploadSamplesCommand(Command, UploadBatchCommandMixin):
    """
    Represents a request to upload a batch of samples along with their associated data.

    The data are uploaded as a single atomic unit of work, so that either all data are
    successfully uploaded or none are.

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
    calculate_distances: bool = Field(
        default=True,
        description=(
            "If False, skip distance calculation for newly uploaded profiles. "
            "Callers uploading many batches in bulk should set this to False and call "
            "UpdateSeqDistancesCommand once at the end."
        ),
    )
    seq_distance_last_modified_at: datetime.datetime | None = Field(
        default=None,
        description=(
            "If provided, the upload will fail if any SeqDistance was modified after this timestamp, "
            " to prevent concurrent modification conflicts."
        ),
    )
    # TODO: is a temporary option, to be removed once the memory handling is handled properly server-side
    existing_chunk_size: int | None = Field(
        default=None,
        description=(
            "If set, existing profiles are processed in chunks of this size "
            "during distance calculation to limit memory use. When None, all "
            "existing profiles are loaded in a single pass (original behaviour)."
        ),
    )
    # TODO: is a temporary option, to be removed once the numpy-vectorised ALLELE distance calculation (or any other that is eventually chosen) is fully validated and deployed. It is intended to allow testing of the new implementation without affecting existing behaviour.
    use_numpy_allele_distance: bool = Field(
        default=False,
        description=(
            "If True, use numpy-vectorised ALLELE Hamming with an automatic "
            "variant gate: numpy_batch for n_new < 200, int32_vocab for "
            "n_new >= 200. No effect on non-ALLELE profile types."
        ),
    )


class RetrieveSeqDistanceLastModifiedCommand(Command):
    """
    Represents a request to retrieve the last modified datetime for a SeqDistance protocol.

    This command is intended to be used in conjunction with the
    CalculateSeqDistancesForNewProfilesCommand command, which has a
    seq_distance_last_modified_at field that can be filled with the return value of this
    command to prevent concurrent modification conflicts by ensuring that no SeqDistance
    was modified after the specified datetime between the time of retrieval and the time
    of calculation and upload of new distances.
    """

    protocol_id: UUID = Field(
        description="The ID of the protocol for which to retrieve the last modified datetune for"
    )


class CalculateSeqDistancesForNewProfilesCommand(Command):
    """
    Represents a request to calculate and store distances between new and existing sequence profiles.

    The calculation uses the given sequence distance protocol and stores
    distances in the database. This command is intended to be used after new profiles
    have been added to the database, in order to calculate and store the distances
    between the new profiles and all existing profiles for later retrieval (e.g. for
    similarity search).
    """

    seq_profiles: list[model.SeqProfile] = Field(
        description="List of new sequence profiles to calculate distances for.",
    )
    seq_distance_last_modified_at: datetime.datetime | None = Field(
        default=None,
        description=(
            "If provided, fail if any SeqDistance was modified after this timestamp."
        ),
    )
    existing_chunk_size: int | None = Field(
        default=None,
        description=(
            "If set, existing profiles are processed in chunks of this size "
            "during distance calculation to limit memory use. When None, all "
            "existing profiles are loaded in a single pass (original behaviour)."
        ),
    )
    use_numpy_allele_distance: bool = Field(
        default=False,
        description=(
            "If True, use numpy-vectorised ALLELE Hamming with an automatic "
            "variant gate: numpy_batch for n_new < 200, int32_vocab for "
            "n_new >= 200. No effect on non-ALLELE profile types."
        ),
    )


class UpdateSeqDistancesCommand(Command):
    """
    Represents a request to create missing distances for profiles under a distance protocol.

    The command finds all profiles
    that do not yet have a SeqDistance record, computes
    the missing distances, and create the records while
    maintaining the symmetry invariant (every distance
    is stored in both directions).
    """

    protocol_id: UUID = Field(
        description=("The ID of the seq distance protocol to update distances for."),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "If set, process at most this many missing profiles per call. "
            "Call repeatedly until the result is empty to process all profiles "
            "incrementally."
        ),
    )
    existing_chunk_size: int | None = Field(
        default=None,
        description=(
            "If set, existing profiles are processed in chunks of this size "
            "to limit memory use. When None, all existing profiles are loaded "
            "and streamed in a single pass (original behaviour)."
        ),
    )
    use_numpy_allele_distance: bool = Field(
        default=False,
        description=(
            "If True, use numpy-vectorised ALLELE Hamming with an automatic "
            "variant gate: numpy_batch for n_new < 200, int32_vocab for "
            "n_new >= 200. No effect on non-ALLELE profile types."
        ),
    )


class CalculatePhylogeneticTreeCommand(Command):
    """
    Represents a request to calculate a phylogenetic tree from query profiles and a configured protocol.

    The returned tree contains the query profiles and
    any additional profiles that are within the maximum distance threshold specified in
    the protocol for at least one of the query profiles. The leaf names in the tree
    correspond to the profile IDs, but can optionally be replaced with custom leaf names
    provided in the command (e.g. for better readability of the tree).

    Model validation: When provided, leaf names must have one entry per queried
    sequence profile.
    """

    protocol_id: UUID = Field(
        description="The ID of the protocol to use for generating the distances"
    )
    tree_algorithm: enum.TreeAlgorithm = Field(
        description="The tree algorithm to use for generating the phylogenetic tree"
    )
    seq_profile_ids: list[UUID] = Field(
        description="List of sequence profile IDs to calculate the phylogenetic tree for"
    )
    leaf_names: list[str] | None = Field(
        default=None,
        description="Optional list of leaf names corresponding to the sequence profile IDs",
    )
    allowed_qc_results: set[enum.QualityControlResult] = Field(
        default=set(enum.QualityControlResultSet.USABLE.value),
        description="Set of allowed quality control results for the profiles to consider in the tree. Only profiles whose qc_result is in this set will be included in the tree. This allows excluding low-quality profiles from the tree.",
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Require custom leaf names to align with the queried profile identifiers."""
        if self.leaf_names is not None and len(self.leaf_names) != len(
            self.seq_profile_ids
        ):
            raise ValueError(
                "leaf_names must be None or have the same length as sequence profile IDs"
            )
        return self


class RetrieveSamplesByQueryCommand(Command):
    """
    Represents a request to retrieve sample identifiers matching a query.

    These identifiers can then be used to retrieve
    the corresponding samples.
    """

    sample_query: model.SampleQuery = Field(
        description="The query to filter samples by."
    )


class RetrieveSamplesByIdCommand(Command):
    """
    Represents a request to retrieve complete data for sample identifiers.

    The result contains FullSample
    objects in the same order.
    """

    sample_ids: list[UUID] = Field(
        description="IDs of the samples to retrieve. Must be unique.",
    )

    @field_validator("sample_ids", mode="after")
    def _validate_sample_ids(cls, sample_ids: list[UUID]) -> list[UUID]:
        """Require every requested sample identifier to occur at most once."""
        if len(set(sample_ids)) != len(sample_ids):
            raise ValueError("sample_ids must be unique")
        return sample_ids


class RetrieveSampleIdentifiersByIdCommand(Command):
    """
    Represents a request to retrieve only SampleIdentifier records for sample identifiers.

    Lighter than RetrieveSamplesByIdCommand — no sequences or read sets.
    """

    sample_ids: list[UUID] = Field(
        description="IDs of the samples to retrieve identifiers for. Must be unique.",
    )

    @field_validator("sample_ids", mode="after")
    def _validate_sample_ids(cls, sample_ids: list[UUID]) -> list[UUID]:
        """Require every requested sample identifier to occur at most once."""
        if len(set(sample_ids)) != len(sample_ids):
            raise ValueError("sample_ids must be unique")
        return sample_ids


class RetrieveSeqFastaCommand(Command):
    """Represents a request to retrieve sequences in FASTA format.

    The result is an iterable that yields one contig at a time.
    """

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )
    wrap: int | None = Field(
        default=80,
        description="Number of characters to wrap the sequence lines.",
    )


class ConvertSeqFormatCommand(Command):
    """Represents a request to convert stored contig sequence representations.

    Returns:
      The IDs of the sequences converted to the target format.
    """

    seq_ids: list[UUID] = Field(
        description="IDs of the sequences whose contigs should be converted.",
    )
    from_format: enum.SeqFormat = Field(
        description="The current DNA representation format of all contigs.",
    )
    to_format: enum.SeqFormat = Field(
        description="The target DNA representation format for all contigs.",
    )

    @field_validator("seq_ids", mode="after")
    @classmethod
    def _validate_seq_ids(cls, seq_ids: list[UUID]) -> list[UUID]:
        """Require every requested sequence identifier to occur at most once."""
        if len(set(seq_ids)) != len(seq_ids):
            raise ValueError("seq_ids must be unique")
        return seq_ids

    @model_validator(mode="after")
    def _validate_formats(self) -> Self:
        """Require a supported, same-family DNA representation conversion."""
        if (
            self.from_format not in enum.SeqFormatSet.DNA_AS_STR.value
            or self.to_format not in enum.SeqFormatSet.DNA_AS_STR.value
        ):
            raise ValueError("Only DNA sequence formats can be converted")
        if (self.from_format in enum.SeqFormatSet.GAP.value) != (
            self.to_format in enum.SeqFormatSet.GAP.value
        ):
            raise ValueError(
                "Conversions between gapless and gap-inclusive formats are not supported"
            )
        return self


class RetrieveSimilarProfilesCommand(Command):
    """
    Represents a request to retrieve profiles similar to at least one query profile.

    the given maximum distance and based on the given seq distance protocol. The
    returned profiles do not contain the query profiles.
    """

    protocol_id: UUID = Field(
        description="ID of the protocol to use for similarity search.",
    )
    profile_ids: list[UUID] = Field(
        description="List of query profile IDs to find similar profiles for.",
    )
    max_distance: float = Field(
        description="Maximum distance threshold for considering profiles as similar.",
    )


class RetrieveBestSeqPerSampleCommand(Command):
    """
    Represents a request to retrieve the best Seq ID for each requested sample.

    IDs, and using a particular ranking strategy.
    Returns a dict[sample_id, seq_id].
    """

    protocol_ids: set[UUID] | None = Field(
        default=None,
        description="The IDs of the assembly protocols to search among. If None, search among all seqs.",
    )
    sample_ids: set[UUID] | None = Field(
        description="The IDs of the samples to search among. If None, search among all samples.",
    )
    ranking_strategy: enum.SeqProfileRankingStrategy = Field(
        default=enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        description="The strategy to use for ranking the profiles. This determines how the best profile is selected.",
    )


class RetrieveBestSeqProfilePerSampleCommand(Command):
    """
    Represents a request to retrieve the best SeqProfile ID for each requested sample.

    protocol IDs, and using a particular ranking strategy.
    Returns a dict[sample_id, seq_profile_id].
    """

    protocol_ids: set[UUID] = Field(
        description="The IDs of the sequence profile protocols to search among.",
        min_length=1,
    )
    sample_ids: set[UUID] | None = Field(
        description="The IDs of the samples to search among. If None, search among all samples.",
    )
    ranking_strategy: enum.SeqProfileRankingStrategy = Field(
        default=enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        description="The strategy to use for ranking the profiles. This determines how the best profile is selected.",
    )


class RetrieveBestSeqClassificationPerSampleCommand(Command):
    """
    Represents a request to retrieve the best SeqClassification ID for each requested sample.

    protocol IDs, and using a particular ranking strategy.
    Returns a dict[sample_id, seq_classification_id].
    """

    protocol_ids: set[UUID] = Field(
        description="The IDs of the sequence classification protocols to search among.",
        min_length=1,
    )
    sample_ids: set[UUID] | None = Field(
        description="The IDs of the samples to search among. If None, search among all samples.",
    )
    ranking_strategy: enum.SeqClassificationRankingStrategy = Field(
        default=enum.SeqClassificationRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        description="The strategy to use for ranking the classifications. This determines how the best classification is selected.",
    )
    return_primary_category_id: bool = Field(
        default=False,
        description="If True, return the primary category ID of the best classification, rather than the ID of the best classification. This facilitates the most frequent use casees where the primary category is the desired output.",
    )


# CRUD commands


class ProtocolCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Protocols."""

    MODEL_CLASS: ClassVar = model.Protocol


class ProtocolSetCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on ProtocolSets."""

    MODEL_CLASS: ClassVar = model.ProtocolSet


class ProtocolSetMemberCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on ProtocolSetMembers."""

    MODEL_CLASS: ClassVar = model.ProtocolSetMember


class AlleleCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Alleles."""

    MODEL_CLASS: ClassVar = model.Allele


class AstMeasurementCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on AstMeasurements."""

    MODEL_CLASS: ClassVar = model.AstMeasurement


class AstPredictionCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on AstPredictions."""

    MODEL_CLASS: ClassVar = model.AstPrediction


class LocusCodeMapCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on LocusCodeMaps."""

    MODEL_CLASS: ClassVar = model.LocusCodeMap


class LocusCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Loci."""

    MODEL_CLASS: ClassVar = model.Locus


class LocusSetCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on LocusSets."""

    MODEL_CLASS: ClassVar = model.LocusSet


class PcrMeasurementCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on PcrMeasurements."""

    MODEL_CLASS: ClassVar = model.PcrMeasurement


class ReadSetCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on ReadSets."""

    MODEL_CLASS: ClassVar = model.ReadSet


class ReadSetIdentifierCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on ReadSetIdentifiers."""

    MODEL_CLASS: ClassVar = model.ReadSetIdentifier


class RefAlleleCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on RefAlleles."""

    MODEL_CLASS: ClassVar = model.RefAllele


class RefSeqCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on RefSeqs."""

    MODEL_CLASS: ClassVar = model.RefSeq


class SampleCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Samples."""

    MODEL_CLASS: ClassVar = model.Sample


class SampleDataCollectionLinkCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SampleDataCollectionLinks."""

    MODEL_CLASS: ClassVar = model.SampleDataCollectionLink


class SampleIdentifierCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SampleIdentifiers."""

    MODEL_CLASS: ClassVar = model.SampleIdentifier


class SeqClassificationCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqClassifications."""

    MODEL_CLASS: ClassVar = model.SeqClassification


class SeqCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Seqs."""

    MODEL_CLASS: ClassVar = model.Seq


class SeqCategoryCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqCategories."""

    MODEL_CLASS: ClassVar = model.SeqCategory


class SeqCategorySetCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqCategorySets."""

    MODEL_CLASS: ClassVar = model.SeqCategorySet


class SeqDistanceCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqDistances."""

    MODEL_CLASS: ClassVar = model.SeqDistance


class SeqIdentifierCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqIdentifiers."""

    MODEL_CLASS: ClassVar = model.SeqIdentifier


class SeqProfileCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqProfiles."""

    MODEL_CLASS: ClassVar = model.SeqProfile


class SeqProfileIdentifierCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqProfileIdentifiers."""

    MODEL_CLASS: ClassVar = model.SeqProfileIdentifier


class SeqTaxonomyCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on SeqTaxonomies."""

    MODEL_CLASS: ClassVar = model.SeqTaxonomy


class TaxonCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on Taxa."""

    MODEL_CLASS: ClassVar = model.Taxon


class TaxonSetCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on TaxonSets."""

    MODEL_CLASS: ClassVar = model.TaxonSet


class TaxonSetMemberCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on TaxonSetMembers."""

    MODEL_CLASS: ClassVar = model.TaxonSetMember


class TreeAlgorithmCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on TreeAlgorithms."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithm


class TreeAlgorithmClassCrudCommand(CrudCommand):
    """Represents a request to perform a CRUD operation on TreeAlgorithmClasses."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass
