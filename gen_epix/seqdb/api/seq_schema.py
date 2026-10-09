"""Request and response models of the seqdb sequence API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, model_validator

from gen_epix.commondb.domain.literal import (
    MAX_CODE_FIELD_LENGTH,
    MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
)
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.util import copy_model_field


class UploadSamplesRequestBody(command.UploadSamplesCommand):
    """Docstring assigned programmatically."""

    __doc__ = command.UploadSamplesCommand.__doc__

    # TODO: SampleBatchForUpload.samples should be restricted in length as well as any other subfields to harden against large payloads.
    sample_batch: model.SampleBatchForUpload = copy_model_field(
        command.UploadSamplesCommand, "sample_batch"
    )
    calculate_distances: bool = copy_model_field(
        command.UploadSamplesCommand, "calculate_distances"
    )
    seq_distance_last_modified_at: datetime | None = copy_model_field(
        command.UploadSamplesCommand, "seq_distance_last_modified_at"
    )
    # TODO: is a temporary option, to be removed once the memory handling is handled properly server-side
    existing_chunk_size: int | None = copy_model_field(
        command.UploadSamplesCommand, "existing_chunk_size"
    )
    # TODO: is a temporary option, to be removed once the numpy-vectorised ALLELE distance calculation (or any other that is eventually chosen) is fully validated and deployed. It is intended to allow testing of the new implementation without affecting existing behaviour.
    use_numpy_allele_distance: bool = copy_model_field(
        command.UploadSamplesCommand, "use_numpy_allele_distance"
    )


class CalculatePhylogeneticTreeRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.CalculatePhylogeneticTreeCommand.__doc__

    protocol_id: UUID = copy_model_field(
        command.CalculatePhylogeneticTreeCommand, "protocol_id"
    )
    tree_algorithm: enum.TreeAlgorithm = copy_model_field(
        command.CalculatePhylogeneticTreeCommand, "tree_algorithm"
    )
    seq_profile_ids: list[UUID] = copy_model_field(
        command.CalculatePhylogeneticTreeCommand,
        "seq_profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    leaf_names: list[str] | None = copy_model_field(
        command.CalculatePhylogeneticTreeCommand,
        "leaf_names",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSimilarProfilesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSimilarProfilesCommand.__doc__

    protocol_id: UUID = copy_model_field(
        command.RetrieveSimilarProfilesCommand, "protocol_id"
    )
    profile_ids: list[UUID] = copy_model_field(
        command.RetrieveSimilarProfilesCommand,
        "profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    max_distance: float = copy_model_field(
        command.RetrieveSimilarProfilesCommand, "max_distance"
    )


class UpdateSeqDistancesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.UpdateSeqDistancesCommand.__doc__
    protocol_id: UUID = copy_model_field(
        command.UpdateSeqDistancesCommand, "protocol_id"
    )
    # TODO: remove max_new_profiles usage and replace by limit
    max_new_profiles: int | None = copy_model_field(
        command.UpdateSeqDistancesCommand, "limit"
    )
    limit: int | None = copy_model_field(command.UpdateSeqDistancesCommand, "limit")
    existing_chunk_size: int | None = copy_model_field(
        command.UpdateSeqDistancesCommand, "existing_chunk_size"
    )
    use_numpy_allele_distance: bool = copy_model_field(
        command.UpdateSeqDistancesCommand, "use_numpy_allele_distance"
    )

    # TODO: remove max_new_profiles usage and replace by limit
    @model_validator(mode="after")
    def validate_limit(self) -> Self:
        """Normalize the deprecated maximum-profile field into ``limit``."""
        if self.limit is None:
            self.limit = self.max_new_profiles
        return self


class RetrieveSeqDistancesBySeqProfilesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSeqDistancesBySeqProfilesCommand.__doc__

    seq_profile_ids: list[UUID] = copy_model_field(
        command.RetrieveSeqDistancesBySeqProfilesCommand,
        "seq_profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    protocol_id: UUID = copy_model_field(
        command.RetrieveSeqDistancesBySeqProfilesCommand, "protocol_id"
    )


class RetrieveSamplesByIdsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSamplesByIdCommand.__doc__
    sample_ids: list[UUID] = copy_model_field(
        command.RetrieveSamplesByIdCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSampleIdentifiersByIdsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSampleIdentifiersByIdCommand.__doc__
    sample_ids: list[UUID] = copy_model_field(
        command.RetrieveSampleIdentifiersByIdCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSeqFastaRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSeqFastaCommand.__doc__

    seq_ids: list[UUID] = copy_model_field(
        command.RetrieveSeqFastaCommand,
        "seq_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    wrap: int = copy_model_field(command.RetrieveSeqFastaCommand, "wrap")
    file_name: str = Field(
        description="The desired filename for the FASTA download.",
        max_length=MAX_CODE_FIELD_LENGTH,
    )


class ConvertSeqFormatRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.ConvertSeqFormatCommand.__doc__

    seq_ids: list[UUID] = copy_model_field(
        command.ConvertSeqFormatCommand,
        "seq_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    from_format: enum.SeqFormat = copy_model_field(
        command.ConvertSeqFormatCommand, "from_format"
    )
    to_format: enum.SeqFormat = copy_model_field(
        command.ConvertSeqFormatCommand, "to_format"
    )


class RetrieveBestSeqPerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqPerSampleCommand.__doc__

    protocol_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveBestSeqProfilePerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqProfilePerSampleCommand.__doc__

    protocol_ids: set[UUID] = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveBestSeqClassificationPerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqClassificationPerSampleCommand.__doc__

    protocol_ids: set[UUID] = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    ranking_strategy: enum.SeqClassificationRankingStrategy = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand, "ranking_strategy"
    )
    return_primary_category_id: bool = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "return_primary_category_id",
    )
