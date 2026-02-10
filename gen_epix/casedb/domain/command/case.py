from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_validator, model_validator

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.command import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter
from gen_epix.seqdb.domain import enum as seqdb_enum

# Non-CRUD


class CaseTypeSetCaseTypeUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeSetMember]


class CaseTypeColSetCaseTypeColUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.CaseTypeColSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_col_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_col_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeColSetMember]


class CreateCaseSetCommand(Command):
    """
    Create a new case set and associate it with the specified data collections and
    cases.
    """

    case_set: model.CaseSet = Field(description="The case set to create.")
    data_collection_ids: set[UUID] = Field(
        description="The data collections to associate with the case set, other than the created_in_data_collection. The latter will be removed from the set if present.",
    )
    case_ids: set[UUID] | None = Field(
        description="The cases to associate with the case set upon creation, if any. These cases must have the same case type as the case set.",
        default=None,
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        self.data_collection_ids.discard(self.case_set.created_in_data_collection_id)
        return self


class UploadCasesCommand(Command, UploadBatchCommandMixin):
    """
    Upload a batch of cases along with their associated data and return an upload
    result. The upload can be stopped after the verification step by setting the
    'verify_only' property to True, so that the returned upload result only contains
    the verification results.

    The data are uploaded as a single atomic unit of work, so that
    either all data are successfully uploaded or none are.
    """

    BATCH_FOR_UPLOAD_CLASS: ClassVar = model.CaseBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "case_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = model.CaseBatchUploadResult

    case_type_id: UUID = Field(
        description="The case type ID that all the cases must belong to. All cases in the case set must have this case type ID."
    )
    created_in_data_collection_id: UUID = Field(
        description="The created in data collection ID that all the cases must belong to. All cases in the case set must have this created in data collection ID."
    )
    case_batch: model.CaseBatchForUpload = Field(
        description="The unique cases to validate."
    )

    @model_validator(mode="after")
    def _validate_cases(self) -> Self:
        cases_for_upload = self.case_batch.cases
        cases = [x.case for x in cases_for_upload if x.case is not None]
        if any(x.case_type_id != self.case_type_id for x in cases):
            raise ValueError("All cases must belong to the given case type ID.")
        if any(
            x.created_in_data_collection_id != self.created_in_data_collection_id
            for x in cases
        ):
            raise ValueError(
                "All cases must belong to the given created_in_data_collection_id."
            )
        return self


class RetrieveCaseStatsCommand(Command):
    """
    Retrieve statistics for a set of case types. Each of the parameters, when
    provided, will further filter the cases that are considered for the
    statistics.
    """

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The case type ids to retrieve stats for, if not all.",
    )
    case_set_ids: list[UUID] | None = Field(
        default=None,
        description="The case set ids to retrieve stats for, if not all. UNIQUE",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCompleteCaseTypeCommand(Command):
    """
    Retrieve a complete case type.
    """

    case_type_id: UUID = Field(description="The ID of the case type to retrieve.")


class RetrieveCasesByQueryCommand(Command):
    """
    Retrieve cases based on a query.
    """

    case_query: model.CaseQuery = Field(description="The query to filter cases by.")


class RetrieveCasesByIdCommand(Command):
    """
    Retrieve cases by their IDs.
    """

    case_type_id: UUID = Field(description="The case type id to retrieve cases for.")
    case_ids: list[UUID] = Field(
        description="The case ids to retrieve cases for. All cases must belong to the given case type. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):
    """
    Retrieve access rights for a set of cases.
    """

    case_type_id: UUID = Field(
        description="The case type id to retrieve case access for."
    )
    case_ids: list[UUID] = Field(
        description="The case ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):
    """
    Retrieve access rights for a set of case sets.
    """

    case_set_ids: list[UUID] = Field(
        description="The case set ids to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case set ids")
        return value


class RetrievePhylogeneticTreeBySequencesCommand(Command):
    """
    Calculate a phylogenetic tree based on a set of sequence IDs, a tree algorithm, and
    a sequence distance protocol.
    """

    tree_algorithm_code: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    seqdb_seq_distance_protocol_id: UUID = Field(
        description="The ID of the sequence distance protocol to use."
    )
    profile_ids: list[UUID] = Field(
        description="The IDs of the profiles to calculate the phylogenetic tree for."
    )


class RetrievePhylogeneticTreeByCasesCommand(Command):
    """
    Retrieve a phylogenetic tree based on a set of case IDs, a tree algorithm, and
    a genetic distance case type column.
    """

    case_type_id: UUID = Field(
        description="The case type ID that all the cases must belong to."
    )
    tree_algorithm: enum.TreeAlgorithmType = Field(
        description="The algorithm to use for constructing the phylogenetic tree."
    )
    genetic_distance_case_type_col_id: UUID = Field(
        description="The ID of the genetic distance case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to calculate the phylogenetic tree for."
    )


class RetrieveSimilarCasesCommand(Command):
    """
    Retrieve cases that are (genetically) similar to a given list of case_ids,
    based on the genetic distance values in a specified genetic distance case type column and a maximum distance threshold.
    """

    case_type_id: UUID = Field(
        description="The case type ID that all the cases must belong to."
    )

    max_distance: float = Field(
        description="The maximum genetic distance for cases to be considered similar.",
        default=5,
    )
    case_ids: list[UUID] = Field(
        description="The IDs of cases to get the similar cases for.",
    )
    genetic_distance_case_type_col_id: UUID = Field(
        description="The case type column ID to use for determining the genetic distance between cases."
    )


class RetrieveGeneticSequenceFastaByCaseCommand(Command):
    """
    Retrieve a set of genetic sequences in FASTA format based on a set of case IDs and a genetic
    sequence case type column. An iterator is returned that yields the FASTA lines.
    """

    case_type_id: UUID = Field(
        description="The case type ID that all the cases must belong to."
    )
    genetic_sequence_case_type_col_id: UUID = Field(
        description="The ID of the genetic sequence case type column to use."
    )
    case_ids: list[UUID] = Field(
        description="The IDs of the cases to retrieve genetic sequences for."
    )


class CreateFileForReadSetCommand(Command):
    """
    Create a file for a read set associated with a case.
    """

    is_fwd: bool = Field(
        description="Whether the file is a forward read file.", default=True
    )
    case_id: UUID = Field(description="The ID of the case the read set belongs to.")
    case_type_col_id: UUID = Field(
        description="The ID of the read set case type column."
    )
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
    """
    Create a file for a sequence associated with a case.
    """

    case_id: UUID = Field(description="The ID of the case the sequence belongs to.")
    case_type_col_id: UUID = Field(
        description="The ID of the genetic sequence case type column."
    )
    file_content: bytes = Field(description="The content of the file to create.")
    file_format: seqdb_enum.SeqFileFormat = Field(
        default=seqdb_enum.SeqFileFormat.FASTA,
        description="The format of the sequence file.",
    )
    file_compression: seqdb_enum.FileCompression = Field(
        default=seqdb_enum.FileCompression.NONE,
        description="The compression of the sequence file.",
    )


class RetrieveSequencingProtocolsCommand(Command):
    """
    Retrieve sequencing protocols from seqdb database
    """

    pass


class RetrieveAssemblyProtocolsCommand(Command):
    """
    Retrieve assembly protocols from seqdb database
    """

    pass


# CRUD


class CaseCrudCommand(CrudCommand):
    """Create and manage individual cases with typed content for a case type, subject, and data collection."""

    MODEL_CLASS: ClassVar = model.Case


class CaseDataCollectionLinkCrudCommand(CrudCommand):
    """Attach or detach cases to additional data collections to widen or restrict sharing beyond their origin."""

    MODEL_CLASS: ClassVar = model.CaseDataCollectionLink


class CaseSetCategoryCrudCommand(CrudCommand):
    """Maintain the categories used to tag case sets (e.g., outbreak, surveillance, QA)."""

    MODEL_CLASS: ClassVar = model.CaseSetCategory


class CaseSetCrudCommand(CrudCommand):
    """Create and manage named groups of cases with case type, category, status, and data-collection context."""

    MODEL_CLASS: ClassVar = model.CaseSet


class CaseSetDataCollectionLinkCrudCommand(CrudCommand):
    """Share case sets into additional data collections for cross-group collaboration."""

    MODEL_CLASS: ClassVar = model.CaseSetDataCollectionLink


class CaseSetMemberCrudCommand(CrudCommand):
    """Add or remove cases from a case set, optionally carrying per-member classification."""

    MODEL_CLASS: ClassVar = model.CaseSetMember


class CaseSetStatusCrudCommand(CrudCommand):
    """Define lifecycle/status values for case sets (e.g., draft, active, closed)."""

    MODEL_CLASS: ClassVar = model.CaseSetStatus


class CaseTypeColCrudCommand(CrudCommand):
    """Define the variables (columns) for a case type, including datatype, vocabularies/regions, and genetic-distance settings."""

    MODEL_CLASS: ClassVar = model.CaseTypeCol


class CaseTypeColSetCrudCommand(CrudCommand):
    """Bundle columns into sets used for read/write scopes and default column groupings."""

    MODEL_CLASS: ClassVar = model.CaseTypeColSet


class CaseTypeColSetMemberCrudCommand(CrudCommand):
    """Manage which columns belong to a column set used in policies or UI presets."""

    MODEL_CLASS: ClassVar = model.CaseTypeColSetMember


class CaseTypeCrudCommand(CrudCommand):
    """Define a case type (structure, metadata, and defaults) that all cases of that type must follow."""

    MODEL_CLASS: ClassVar = model.CaseType


class CaseTypeDimCrudCommand(CrudCommand):
    """Define dimensions that group case-type columns (e.g., demographics, sample, sequencing)."""

    MODEL_CLASS: ClassVar = model.CaseTypeDim


class CaseTypeSetCategoryCrudCommand(CrudCommand):
    """Maintain categories used to organize case-type sets for policy scoping."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetCategory


class CaseTypeSetCrudCommand(CrudCommand):
    """Group related case types into reusable sets for access policies and presets."""

    MODEL_CLASS: ClassVar = model.CaseTypeSet


class CaseTypeSetMemberCrudCommand(CrudCommand):
    """Assign or remove case types within a case-type set."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetMember


class ColCrudCommand(CrudCommand):
    """Manage reusable column definitions (code/label/type) that back case-type columns and reference vocabularies."""

    MODEL_CLASS: ClassVar = model.Col


class DimCrudCommand(CrudCommand):
    """Define column dimensions, including code prefixes and ordering, reused across case types."""

    MODEL_CLASS: ClassVar = model.Dim


class GeneticDistanceProtocolCrudCommand(CrudCommand):
    """Register genetic distance protocols (e.g., TN93) available for sequence comparisons in phylogenetic analyses."""

    MODEL_CLASS: ClassVar = model.GeneticDistanceProtocol


class TreeAlgorithmClassCrudCommand(CrudCommand):
    """Register categories of phylogenetic algorithms and whether they require sequences vs. distance matrices."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    """Register specific phylogenetic tree algorithms linked to seqdb implementations and tuning parameters."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithm
