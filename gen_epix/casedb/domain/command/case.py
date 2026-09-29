"""Define casedb commands for case schemas, content, sets, and sequence links."""

from typing import ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.command import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.seqdb.domain import enum as seqdb_enum

# Non-CRUD


class CaseTypeSetCaseTypeUpdateAssociationCommand(UpdateAssociationCommand):
    """Represents a request to replace the association between a case type set and its
    case types.

    The provided members keep the set synchronized for downstream access
    policies and presets.
    """

    ASSOCIATION_CLASS: ClassVar = model.CaseTypeSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeSetMember]


class ColSetColUpdateAssociationCommand(UpdateAssociationCommand):
    """Represents a request to replace the association between a column set and its columns.

    The provided members keep read/write scopes and user-interface column
    groupings aligned.
    """

    ASSOCIATION_CLASS: ClassVar = model.ColSetMember
    LINK_FIELD_NAME1: ClassVar = "col_set_id"
    LINK_FIELD_NAME2: ClassVar = "col_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.ColSetMember]


class CreateCaseSetCommand(Command):
    """Represents a request to create a case set and its initial associations.

    Model validation:
        The creating data collection is removed from the additional data
        collections because it is already associated through the case set.
    """

    case_set: model.CaseSet = Field(description="The case set to create.")
    data_collection_ids: set[UUID] = Field(
        description="The data collections to associate with the case set, other than the created_in_data_collection. The latter will be removed from the set if present.",
        default_factory=set,
    )
    case_ids: set[UUID] | None = Field(
        description="The cases to associate with the case set upon creation, if any. These cases must have the same CaseType as the case set.",
        default=None,
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Remove the creating data collection from additional associations."""
        self.data_collection_ids.discard(self.case_set.created_in_data_collection_id)
        return self


class UploadCasesCommand(Command, UploadBatchCommandMixin):
    """Represents a request to perform an atomic batch upload of cases and associated data.

    The upload returns an upload result. Setting ``verify_only`` stops processing
    after verification, so the result contains only verification outcomes.

    The data are uploaded as a single atomic unit of work, so that
    either all data are successfully uploaded or none are.

    Model validation:
        Every supplied case must belong to the command's case type. A mismatched
        case causes validation to fail.
    """

    BATCH_FOR_UPLOAD_CLASS: ClassVar = model.CaseBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "case_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = model.CaseBatchUploadResult

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to. All cases in the case set must have this CaseType ID."
    )
    default_created_in_data_collection_id: UUID = Field(
        default=NULL_ID,
        description="The default data collection to associate with the cases if not specified at the case level AND the case does not exist yet.",
    )
    case_batch: model.CaseBatchForUpload = Field(
        description="The unique cases to validate."
    )

    @model_validator(mode="after")
    def _validate_cases(self) -> Self:
        """Ensure every supplied case belongs to the command's case type."""
        cases_for_upload = self.case_batch.cases
        cases = [x.case for x in cases_for_upload if x.case is not None]
        if any(x.case_type_id != self.case_type_id for x in cases):
            raise ValueError("All cases must belong to the given CaseType ID.")
        return self


class RetrieveCaseTypeStatsCommand(Command):
    """Represents a request to retrieve statistics about case types.

    Optional parameters further filter the cases considered for the statistics.
    """

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The CaseType IDs to retrieve stats for, if not all.",
    )
    datetime_range_filter: DatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute of the filter should be left empty.",
    )


class RetrieveCaseSetStatsCommand(Command):
    """Represents a request to retrieve statistics about case sets.

    Optional parameters further filter the cases considered for the statistics.
    """

    case_set_ids: set[UUID] | None = Field(
        default=None,
        description="The case set IDs to retrieve stats for, if not all.",
    )
    datetime_range_filter: DatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute of the filter should be left empty.",
    )


class RetrieveCompleteCaseTypeCommand(Command):
    """Represents a request to retrieve a complete case type."""

    case_type_id: UUID = Field(description="The ID of the CaseType to retrieve.")


class RetrieveCasesByQueryCommand(Command):
    """Represents a request to retrieve cases matching a case query."""

    case_query: model.CaseQuery = Field(description="The query to filter cases by.")


class RetrieveCaseCohortLinksByCaseTypeCommand(Command):
    """Represents a request to retrieve case-to-cohort links for a case type.

    The request returns every case without pagination and is restricted to the
    application administrator role.
    """

    case_type_id: UUID = Field(description="The CaseType ID to retrieve pairs for.")
    include_missing: bool = Field(
        default=False,
        description="Whether to include cases that have no linked cohorts, with NULL_ID as the cohort_id and cohort_definition_id.",
    )


class RetrieveCasesByIdCommand(Command):
    """Represents a request to retrieve cases identified by unique IDs."""

    case_type_id: UUID = Field(description="The CaseType ID to retrieve cases for.")
    case_ids: list[UUID] = Field(
        description="The case IDs to retrieve cases for. All cases must belong to the given CaseType. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    @classmethod
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        """Ensure the requested case IDs are unique."""
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):
    """Represents a request to retrieve access rights to specified cases."""

    case_type_id: UUID = Field(
        description="The CaseType ID to retrieve case access for."
    )
    case_ids: list[UUID] = Field(
        description="The Case IDs to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    @classmethod
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        """Ensure the case IDs used for access lookup are unique."""
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):
    """Represents a request to retrieve access rights to specified case sets."""

    case_set_ids: list[UUID] = Field(
        description="The CaseSet IDs to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    @classmethod
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        """Ensure the case-set IDs used for access lookup are unique."""
        if len(set(value)) < len(value):
            raise ValueError("Duplicate CaseSet IDs")
        return value


class RetrievePhylogeneticTreeByProfilesCommand(Command):
    """Represents a request to calculate a phylogenetic tree from sequence profiles."""

    tree_algorithm_code: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    seqdb_protocol_id: UUID = Field(description="The ID of the protocol to use.")
    profile_ids: list[UUID] = Field(
        description="The IDs of the profiles to calculate the phylogenetic tree for."
    )
    allowed_qc_results: set[seqdb_enum.QualityControlResult] = Field(
        default=set(seqdb_enum.QualityControlResultSet.USABLE.value),
        description="Set of allowed quality control results for the profiles to consider in the tree. Only profiles whose qc_result is in this set will be included in the tree. This allows excluding low-quality profiles from the tree.",
    )


class RetrievePhylogeneticTreeByCasesCommand(Command):
    """Represents a request to calculate a phylogenetic tree from cases and genetic distances."""

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to."
    )
    tree_algorithm: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    genetic_distance_col_id: UUID = Field(
        description="The ID of the genetic distance Col to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to calculate the phylogenetic tree for."
    )
    allowed_qc_results: set[seqdb_enum.QualityControlResult] = Field(
        default=set(seqdb_enum.QualityControlResultSet.ALL.value),
        description="Set of allowed quality control results for the profiles to consider in the tree. Only profiles whose qc_result is in this set will be included in the tree. This allows excluding low-quality profiles from the tree.",
    )


class RetrieveSimilarCasesCommand(Command):
    """Represents a request to retrieve genetically similar cases.

    Similarity is based on a genetic-distance column and a maximum distance
    threshold applied to the supplied case IDs.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to."
    )

    max_distance: float = Field(
        description="The maximum genetic distance for cases to be considered similar.",
        ge=0,
    )
    genetic_distance_col_id: UUID = Field(
        description="The Col ID to use for determining the genetic distance between cases."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of cases to get the similar cases for.",
    )


class RetrieveSimilarCasesReturnValue(BaseModel):
    """Represents the cases returned by a similar-case request."""

    cases: list[model.SimilarCase] = Field(
        description="The similar cases that were found, limited to their IDs and case dates."
    )


class RetrieveGeneticSequenceFastaByCaseCommand(Command):
    """Represents a request for case-linked sequences in FASTA format.

    The response is an iterator that yields FASTA lines for sequences selected
    through the specified genetic-sequence column.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to."
    )
    genetic_sequence_col_id: UUID = Field(
        description="The ID of the genetic sequence Col to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to retrieve genetic sequences for."
    )


class CreateFileForReadSetCommand(Command):
    """Represents a request to upload a raw-reads file for a case read-set column.

    The command accepts base64 content with optional compression, distinguishes
    forward from reverse reads, and returns the stored file ID.
    """

    is_fwd: bool = Field(
        description="Whether the file is a forward read file.", default=True
    )
    case_id: UUID = Field(description="The ID of the case the read set belongs to.")
    col_id: UUID = Field(description="The ID of the read set Col.")
    file_content: bytes = Field(description="The content of the file to create.")
    file_format: seqdb_enum.ReadsFileFormat = Field(
        default=seqdb_enum.ReadsFileFormat.FASTQ,
        description="The format of the reads file.",
    )
    file_compression: seqdb_enum.FileCompression = Field(
        default=seqdb_enum.FileCompression.NONE,
        description="The compression of the reads file.",
    )


class CreateFileForSeqCommand(Command):
    """Represents a request to upload an assembled file for a case sequence column.

    The command accepts base64 content with optional compression and returns the
    stored file ID.
    """

    case_id: UUID = Field(description="The ID of the case the sequence belongs to.")
    col_id: UUID = Field(description="The ID of the genetic sequence Col.")
    file_content: bytes = Field(description="The content of the file to create.")
    file_format: seqdb_enum.SeqFileFormat = Field(
        default=seqdb_enum.SeqFileFormat.FASTA,
        description="The format of the sequence file.",
    )
    file_compression: seqdb_enum.FileCompression = Field(
        default=seqdb_enum.FileCompression.NONE,
        description="The compression of the sequence file.",
    )


class RetrieveProtocolsCommand(Command):
    """Represents a request to retrieve seqdb protocols by protocol type."""

    protocol_type: seqdb_enum.ProtocolType = Field(
        description="The type of protocols to retrieve."
    )


class RetrieveIsOwnCasesCommand(Command):
    """Represents a request to retrieve cases owned by or accessible to the user.

    The response contains the supplied case IDs that the user owns or may access.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to check ownership for."
    )


class UpdateCaseCreatedInDataCollectionCommand(Command):
    """Represents a request to assign a different created_in_data_collection_id to a list of cases."""

    case_ids: list[UUID] = Field(description="The IDs of the cases to update.")
    target_created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection to assign to the cases as created_in_data_collection_id."
    )


# CRUD


class CaseCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on Cases."""

    MODEL_CLASS: ClassVar = model.Case


class CaseIdentifierCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseIdentifiers."""

    MODEL_CLASS: ClassVar = model.CaseIdentifier


class CaseDataCollectionLinkCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseDataCollection links."""

    MODEL_CLASS: ClassVar = model.CaseDataCollectionLink


class CaseSetCategoryCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseSetCategories."""

    MODEL_CLASS: ClassVar = model.CaseSetCategory


class CaseSetCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseSets."""

    MODEL_CLASS: ClassVar = model.CaseSet


class CaseSetDataCollectionLinkCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseSetDataCollectionLinks."""

    MODEL_CLASS: ClassVar = model.CaseSetDataCollectionLink


class CaseSetMemberCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseSetMembers."""

    MODEL_CLASS: ClassVar = model.CaseSetMember


class CaseSetStatusCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseSetStatuses."""

    MODEL_CLASS: ClassVar = model.CaseSetStatus


class ColCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on Cols."""

    MODEL_CLASS: ClassVar = model.Col


class ColSetCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on ColSets."""

    MODEL_CLASS: ClassVar = model.ColSet


class ColSetMemberCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on ColSetMembers."""

    MODEL_CLASS: ClassVar = model.ColSetMember


class CaseTypeCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseTypes."""

    MODEL_CLASS: ClassVar = model.CaseType


class DimCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on Dims."""

    MODEL_CLASS: ClassVar = model.Dim


class CaseTypeSetCategoryCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseTypeSetCategories."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetCategory


class CaseTypeSetCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseTypeSets."""

    MODEL_CLASS: ClassVar = model.CaseTypeSet


class CaseTypeSetMemberCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on CaseTypeSetMembers."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetMember


class RefColCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on RefCols."""

    MODEL_CLASS: ClassVar = model.RefCol


class RefDimCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on RefDims."""

    MODEL_CLASS: ClassVar = model.RefDim


class GeneticDistanceProtocolCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on GeneticDistanceProtocols."""

    MODEL_CLASS: ClassVar = model.GeneticDistanceProtocol


class TreeAlgorithmClassCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on TreeAlgorithmClasses."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    """Represents a request to execute a CRUD operation on TreeAlgorithms."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithm
