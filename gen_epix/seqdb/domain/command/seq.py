"""Define commands for SeqDB sequence workflows and managed domain records.

The command types carry input for upload, distance, tree, similarity, and
sample retrieval operations, plus CRUD metadata for SeqDB sequence models.
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
    Upload a batch of samples along with their associated data.

    The data are uploaded
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
    Retrieve the last modified datetime for a SeqDistance protocol.

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
    Calculate and store distances between new and existing sequence profiles.

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
    Create missing distances for profiles under a distance protocol.

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
    Calculate a phylogenetic tree from query profiles and a configured protocol.

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
    Retrieve sample identifiers matching a query.

    These identifiers can then be used to retrieve
    the corresponding samples.
    """

    sample_query: model.SampleQuery = Field(
        description="The query to filter samples by."
    )


class RetrieveSamplesByIdCommand(Command):
    """
    Retrieve complete data for sample identifiers.

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
    Retrieve only SampleIdentifier records for sample identifiers.

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
    """
    Retrieve sequences in FASTA format.

    as an iterable that yields one contig at a time.
    """

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )
    wrap: int | None = Field(
        default=80,
        description="Number of characters to wrap the sequence lines.",
    )


class RetrieveSimilarProfilesCommand(Command):
    """
    Retrieve profiles similar to at least one query profile.

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
    Retrieve the best Seq ID for each requested sample.

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
    Retrieve the best SeqProfile ID for each requested sample.

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
    Retrieve the best SeqClassification ID for each requested sample.

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
    """Provide CRUD command metadata for sequence protocol records."""

    MODEL_CLASS: ClassVar = model.Protocol


class ProtocolSetCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence protocol-set records."""

    MODEL_CLASS: ClassVar = model.ProtocolSet


class ProtocolSetMemberCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence protocol-set memberships."""

    MODEL_CLASS: ClassVar = model.ProtocolSetMember


class AlleleCrudCommand(CrudCommand):
    """Provide CRUD command metadata for allele records."""

    MODEL_CLASS: ClassVar = model.Allele


class AstMeasurementCrudCommand(CrudCommand):
    """Provide CRUD command metadata for antimicrobial-susceptibility measurements."""

    MODEL_CLASS: ClassVar = model.AstMeasurement


class AstPredictionCrudCommand(CrudCommand):
    """Provide CRUD command metadata for antimicrobial-susceptibility predictions."""

    MODEL_CLASS: ClassVar = model.AstPrediction


class LocusCodeMapCrudCommand(CrudCommand):
    """Provide CRUD command metadata for locus-code mapping records."""

    MODEL_CLASS: ClassVar = model.LocusCodeMap


class LocusCrudCommand(CrudCommand):
    """Provide CRUD command metadata for locus records."""

    MODEL_CLASS: ClassVar = model.Locus


class LocusSetCrudCommand(CrudCommand):
    """Provide CRUD command metadata for locus-set records."""

    MODEL_CLASS: ClassVar = model.LocusSet


class PcrMeasurementCrudCommand(CrudCommand):
    """Provide CRUD command metadata for PCR measurement records."""

    MODEL_CLASS: ClassVar = model.PcrMeasurement


class ReadSetCrudCommand(CrudCommand):
    """Provide CRUD command metadata for read-set records."""

    MODEL_CLASS: ClassVar = model.ReadSet


class ReadSetIdentifierCrudCommand(CrudCommand):
    """Provide CRUD command metadata for read-set identifier records."""

    MODEL_CLASS: ClassVar = model.ReadSetIdentifier


class RefAlleleCrudCommand(CrudCommand):
    """Provide CRUD command metadata for reference allele records."""

    MODEL_CLASS: ClassVar = model.RefAllele


class RefSeqCrudCommand(CrudCommand):
    """Provide CRUD command metadata for reference sequence records."""

    MODEL_CLASS: ClassVar = model.RefSeq


class SampleCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sample records."""

    MODEL_CLASS: ClassVar = model.Sample


class SampleDataCollectionLinkCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sample data-collection links."""

    MODEL_CLASS: ClassVar = model.SampleDataCollectionLink


class SampleIdentifierCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sample identifier records."""

    MODEL_CLASS: ClassVar = model.SampleIdentifier


class SeqClassificationCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence classification records."""

    MODEL_CLASS: ClassVar = model.SeqClassification


class SeqCrudCommand(CrudCommand):
    """Provide CRUD command metadata for assembled sequence records."""

    MODEL_CLASS: ClassVar = model.Seq


class SeqCategoryCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence category records."""

    MODEL_CLASS: ClassVar = model.SeqCategory


class SeqCategorySetCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence category-set records."""

    MODEL_CLASS: ClassVar = model.SeqCategorySet


class SeqDistanceCrudCommand(CrudCommand):
    """Provide CRUD command metadata for pairwise sequence-distance records."""

    MODEL_CLASS: ClassVar = model.SeqDistance


class SeqIdentifierCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence identifier records."""

    MODEL_CLASS: ClassVar = model.SeqIdentifier


class SeqProfileCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence profile records."""

    MODEL_CLASS: ClassVar = model.SeqProfile


class SeqProfileIdentifierCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence profile identifier records."""

    MODEL_CLASS: ClassVar = model.SeqProfileIdentifier


class SeqTaxonomyCrudCommand(CrudCommand):
    """Provide CRUD command metadata for sequence taxonomy records."""

    MODEL_CLASS: ClassVar = model.SeqTaxonomy


class TaxonCrudCommand(CrudCommand):
    """Provide CRUD command metadata for taxon records."""

    MODEL_CLASS: ClassVar = model.Taxon


class TaxonSetCrudCommand(CrudCommand):
    """Provide CRUD command metadata for taxon-set records."""

    MODEL_CLASS: ClassVar = model.TaxonSet


class TaxonSetMemberCrudCommand(CrudCommand):
    """Provide CRUD command metadata for taxon-set membership records."""

    MODEL_CLASS: ClassVar = model.TaxonSetMember


class TreeAlgorithmCrudCommand(CrudCommand):
    """Provide CRUD command metadata for phylogenetic tree algorithm records."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithm


class TreeAlgorithmClassCrudCommand(CrudCommand):
    """Provide CRUD command metadata for tree algorithm class records."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass
