"""Request and response models of the casedb case API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_serializer

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain.literal import (
    MAX_REQUEST_BODY_FILE_CONTENT_LENGTH,
    MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
)
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.util import copy_model_field


class CaseTypeSetCaseTypeUpdateAssociationRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.CaseTypeSetCaseTypeUpdateAssociationCommand.__doc__
    case_type_set_members: list[model.CaseTypeSetMember] = copy_model_field(
        command.CaseTypeSetCaseTypeUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class ColSetColUpdateAssociationRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.ColSetColUpdateAssociationCommand.__doc__
    col_set_members: list[model.ColSetMember] = copy_model_field(
        command.ColSetColUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class CreateCaseSetRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.CreateCaseSetCommand.__doc__
    case_set: model.CaseSet = copy_model_field(command.CreateCaseSetCommand, "case_set")
    data_collection_ids: set[UUID] = copy_model_field(
        command.CreateCaseSetCommand,
        "data_collection_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    case_ids: set[UUID] | None = copy_model_field(
        command.CreateCaseSetCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class UpdateCaseCreatedInDataCollectionRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.UpdateCaseCreatedInDataCollectionCommand.__doc__
    case_ids: list[UUID] = copy_model_field(
        command.UpdateCaseCreatedInDataCollectionCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    target_created_in_data_collection_id: UUID = copy_model_field(
        command.UpdateCaseCreatedInDataCollectionCommand,
        "target_created_in_data_collection_id",
    )


class RetrieveCaseRightsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveCaseRightsCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrieveCaseRightsCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveCaseRightsCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveCasesByIdRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveCasesByIdCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrieveCasesByIdCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveCasesByIdCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveCaseCohortLinksByCaseTypeRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveCaseCohortLinksByCaseTypeCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrieveCaseCohortLinksByCaseTypeCommand, "case_type_id"
    )


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrievePhylogeneticTreeByCasesCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "case_type_id"
    )
    genetic_distance_col_id: UUID = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand,
        "genetic_distance_col_id",
    )
    tree_algorithm_code: enum.TreeAlgorithmType = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "tree_algorithm"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSeqDistancesByCasesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveSeqDistancesByCasesCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrieveSeqDistancesByCasesCommand, "case_type_id"
    )
    genetic_distance_col_id: UUID = copy_model_field(
        command.RetrieveSeqDistancesByCasesCommand, "genetic_distance_col_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveSeqDistancesByCasesCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    filter_other_cases: bool = copy_model_field(
        command.RetrieveSeqDistancesByCasesCommand, "filter_other_cases"
    )


class RetrieveSimilarCasesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveSimilarCasesCommand.__doc__
    case_type_id: UUID = copy_model_field(
        command.RetrieveSimilarCasesCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveSimilarCasesCommand,
        "case_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    genetic_distance_col_id: UUID = copy_model_field(
        command.RetrieveSimilarCasesCommand, "genetic_distance_col_id"
    )
    max_distance: float = copy_model_field(
        command.RetrieveSimilarCasesCommand, "max_distance"
    )


class RetrieveSimilarCasesResponseBody(command.RetrieveSimilarCasesReturnValue):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveSimilarCasesReturnValue.__doc__


class RetrieveCaseTypeStatsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveCaseTypeStatsCommand.__doc__
    case_type_ids: set[UUID] | None = copy_model_field(
        command.RetrieveCaseTypeStatsCommand,
        "case_type_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    datetime_range_filter: DatetimeRangeFilter | None = copy_model_field(
        command.RetrieveCaseTypeStatsCommand, "datetime_range_filter"
    )


class RetrieveCaseSetStatsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.RetrieveCaseSetStatsCommand.__doc__
    case_set_ids: set[UUID] | None = copy_model_field(
        command.RetrieveCaseSetStatsCommand,
        "case_set_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    datetime_range_filter: DatetimeRangeFilter | None = copy_model_field(
        command.RetrieveCaseSetStatsCommand, "datetime_range_filter"
    )


class CreateFileForReadSetRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.CreateFileForReadSetCommand.__doc__
    file_content: str = Field(
        description="The content of the file to create as base64 encoded bytes.",
        max_length=MAX_REQUEST_BODY_FILE_CONTENT_LENGTH,
    )
    is_fwd: bool = Field(
        description="Whether the file is for the forward reads (True) or reverse reads (False).",
    )
    file_format: seqdb_enum.ReadsFileFormat = copy_model_field(
        command.CreateFileForReadSetCommand, "file_format"
    )
    file_compression: seqdb_enum.FileCompression = copy_model_field(
        command.CreateFileForReadSetCommand, "file_compression"
    )


class CreateFileForSeqRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""  # noqa: D415

    __doc__ = command.CreateFileForSeqCommand.__doc__
    file_content: str = Field(
        description="The content of the file to create as base64 encoded bytes.",
        max_length=MAX_REQUEST_BODY_FILE_CONTENT_LENGTH,
    )
    file_format: seqdb_enum.SeqFileFormat = copy_model_field(
        command.CreateFileForSeqCommand, "file_format"
    )
    file_compression: seqdb_enum.FileCompression = copy_model_field(
        command.CreateFileForSeqCommand, "file_compression"
    )


class RefColValidationRulesResponseBody(PydanticBaseModel):
    """Represents additional validation rules for reference columns.

    Model serialization:
        Dimension and column type enum values are serialized as strings, and
        each set of valid column types is serialized as a list.
    """

    valid_col_types_by_dim_type: dict[enum.DimType, set[enum.ColType]] = Field(
        default={enum.DimType[x.name]: set(x.value) for x in enum.DimColTypeSet},
        description="The RefCol.col_type values that are allowed depending on the RefCol.ref_dim.dim_type.",
    )

    @field_serializer("valid_col_types_by_dim_type")
    def serialize_valid_col_types_by_dim_type(
        self, value: dict[enum.DimType, set[enum.ColType]]
    ) -> dict[str, list[str]]:
        """Serialize dim-type keys and col-type sets to plain string dicts."""
        return {x.value: [z.value for z in y] for x, y in value.items()}
