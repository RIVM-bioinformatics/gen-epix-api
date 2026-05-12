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
    """
    Replace the CaseTypes in a CaseTypeSet with the provided list of members,
    keeping the set in sync for downstream access policies and presets.
    """

    ASSOCIATION_CLASS: ClassVar = model.CaseTypeSetMember
    LINK_FIELD_NAME1: ClassVar = "case_type_set_id"
    LINK_FIELD_NAME2: ClassVar = "case_type_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.CaseTypeSetMember]


class ColSetColUpdateAssociationCommand(UpdateAssociationCommand):
    """
    Replace the columns in a ColSet with the provided members so
    read/write scopes and UI column groupings stay aligned.
    """

    ASSOCIATION_CLASS: ClassVar = model.ColSetMember
    LINK_FIELD_NAME1: ClassVar = "col_set_id"
    LINK_FIELD_NAME2: ClassVar = "col_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.ColSetMember]


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
        description="The cases to associate with the case set upon creation, if any. These cases must have the same CaseType as the case set.",
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
        description="The CaseType ID that all the cases must belong to. All cases in the case set must have this CaseType ID."
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
            raise ValueError("All cases must belong to the given CaseType ID.")
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
    Retrieve statistics for a set of CaseTypes. Each of the parameters, when
    provided, will further filter the cases that are considered for the
    statistics.
    """

    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The CaseType IDs to retrieve stats for, if not all.",
    )
    case_set_ids: list[UUID] | None = Field(
        default=None,
        description="The case set IDs to retrieve stats for, if not all. UNIQUE",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCompleteCaseTypeCommand(Command):
    """
    Retrieve a complete CaseType.
    """

    case_type_id: UUID = Field(description="The ID of the CaseType to retrieve.")


class RetrieveCasesByQueryCommand(Command):
    """
    Retrieve cases based on a query.
    """

    case_query: model.CaseQuery = Field(description="The query to filter cases by.")


class RetrieveCaseCohortIdsByCaseTypeCommand(Command):
    """
    Retrieve all (case_id, cohort_ids) pairs for a given CaseType.
    Returns every case without pagination. Restricted to APP_ADMIN.
    Today cohort_id == case_id; in the future a case may have multiple
    linked cohort IDs.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID to retrieve pairs for."
    )


class RetrieveCasesByIdCommand(Command):
    """
    Retrieve cases by their IDs.
    """

    case_type_id: UUID = Field(description="The CaseType ID to retrieve cases for.")
    case_ids: list[UUID] = Field(
        description="The case IDs to retrieve cases for. All cases must belong to the given CaseType. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    @classmethod
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseRightsCommand(Command):
    """
    Retrieve access rights for a set of cases.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID to retrieve case access for."
    )
    case_ids: list[UUID] = Field(
        description="The Case IDs to retrieve access for. UNIQUE"
    )

    @field_validator("case_ids", mode="after")
    @classmethod
    def _validate_case_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate case ids")
        return value


class RetrieveCaseSetRightsCommand(Command):
    """
    Retrieve access rights for a set of case sets.
    """

    case_set_ids: list[UUID] = Field(
        description="The CaseSet IDs to retrieve access for. UNIQUE"
    )

    @field_validator("case_set_ids", mode="after")
    @classmethod
    def _validate_case_set_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(set(value)) < len(value):
            raise ValueError("Duplicate CaseSet IDs")
        return value


class RetrievePhylogeneticTreeByProfilesCommand(Command):
    """
    Calculate a phylogenetic tree based on a set of profile IDs, a tree algorithm, and
    a protocol.
    """

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
    """
    Retrieve a phylogenetic tree based on a set of case IDs, a tree algorithm, and
    a genetic distance Col.
    """

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
    """
    Retrieve cases that are (genetically) similar to a given list of case_ids,
    based on the genetic distance values in a specified genetic distance Col and a maximum distance threshold.
    """

    case_type_id: UUID = Field(
        description="The CaseType ID that all the cases must belong to."
    )

    max_distance: float = Field(
        description="The maximum genetic distance for cases to be considered similar.",
        default=5,
    )
    case_ids: list[UUID] = Field(
        description="The IDs of cases to get the similar cases for.",
    )
    genetic_distance_col_id: UUID = Field(
        description="The Col ID to use for determining the genetic distance between cases."
    )


class RetrieveGeneticSequenceFastaByCaseCommand(Command):
    """
    Retrieve a set of genetic sequences in FASTA format based on a set of case IDs and a genetic
    sequence Col. An iterator is returned that yields the FASTA lines.
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
    """
    Upload a raw reads file (e.g., FASTQ) for a case's read-set column and return
    the stored file ID. Accepts base64 content, optional compression, and marks
    whether the payload is forward or reverse reads.
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
    """
    Upload an assembled sequence file (e.g., FASTA) for a case's sequence column
    and return the stored file ID. Accepts base64 content with optional
    compression.
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
    """
    Retrieve the protocols registered in seqdb for downstream sequence
    processing and provenance.
    """

    protocol_type: seqdb_enum.ProtocolType = Field(
        description="The type of protocols to retrieve."
    )


# CRUD


class CaseCrudCommand(CrudCommand):
    """Manage cases (list/get/create/update/delete) with typed content tied to a CaseType and data collection."""

    MODEL_CLASS: ClassVar = model.Case


class CaseIdentifierCrudCommand(CrudCommand):
    """Manage case identifiers that link cases to external systems or provide alternate lookup keys."""

    MODEL_CLASS: ClassVar = model.CaseIdentifier


class CaseDataCollectionLinkCrudCommand(CrudCommand):
    """Manage links that associate cases with additional data collections to widen or restrict sharing beyond their origin."""

    MODEL_CLASS: ClassVar = model.CaseDataCollectionLink


class CaseSetCategoryCrudCommand(CrudCommand):
    """Maintain the categories used to tag case sets (e.g., outbreak, surveillance, QA)."""

    MODEL_CLASS: ClassVar = model.CaseSetCategory


class CaseSetCrudCommand(CrudCommand):
    """Manage case sets (list/get/create/update/delete) including type, category, status, and data-collection context."""

    MODEL_CLASS: ClassVar = model.CaseSet


class CaseSetDataCollectionLinkCrudCommand(CrudCommand):
    """Manage links that share case sets into additional data collections for cross-group collaboration."""

    MODEL_CLASS: ClassVar = model.CaseSetDataCollectionLink


class CaseSetMemberCrudCommand(CrudCommand):
    """Manage membership of cases in a case set, including per-member classification when present."""

    MODEL_CLASS: ClassVar = model.CaseSetMember


class CaseSetStatusCrudCommand(CrudCommand):
    """Maintain lifecycle/status values for case sets (e.g., draft, active, closed)."""

    MODEL_CLASS: ClassVar = model.CaseSetStatus


class ColCrudCommand(CrudCommand):
    """Manage case-type columns: datatype, vocab/region bindings, and genetic-distance settings."""

    MODEL_CLASS: ClassVar = model.Col


class ColSetCrudCommand(CrudCommand):
    """Manage column sets used for read/write scopes and default column groupings."""

    MODEL_CLASS: ClassVar = model.ColSet


class ColSetMemberCrudCommand(CrudCommand):
    """Manage which columns belong to a column set used in policies or UI presets."""

    MODEL_CLASS: ClassVar = model.ColSetMember


class CaseTypeCrudCommand(CrudCommand):
    """Manage CaseTypes—the structural and default definitions cases must follow."""

    MODEL_CLASS: ClassVar = model.CaseType


class DimCrudCommand(CrudCommand):
    """Manage dimensions that group case-type columns (e.g., demographics, sample, sequencing)."""

    MODEL_CLASS: ClassVar = model.Dim


class CaseTypeSetCategoryCrudCommand(CrudCommand):
    """Maintain categories used to organize case-type sets for policy scoping."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetCategory


class CaseTypeSetCrudCommand(CrudCommand):
    """Manage sets of related CaseTypes reused in access policies and presets."""

    MODEL_CLASS: ClassVar = model.CaseTypeSet


class CaseTypeSetMemberCrudCommand(CrudCommand):
    """Manage which CaseTypes belong to a case-type set."""

    MODEL_CLASS: ClassVar = model.CaseTypeSetMember


class RefColCrudCommand(CrudCommand):
    """Manage reusable column definitions (code/label/type) referenced by case-type columns and vocabularies."""

    MODEL_CLASS: ClassVar = model.RefCol


class RefDimCrudCommand(CrudCommand):
    """Manage column dimensions, including code prefixes and ordering, reused across CaseTypes."""

    MODEL_CLASS: ClassVar = model.RefDim


class GeneticDistanceProtocolCrudCommand(CrudCommand):
    """Manage genetic distance protocols available for sequence comparisons in phylogenetic analyses."""

    MODEL_CLASS: ClassVar = model.GeneticDistanceProtocol


class TreeAlgorithmClassCrudCommand(CrudCommand):
    """Manage categories of phylogenetic algorithms and whether they require sequences vs. distance matrices."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithmClass


class TreeAlgorithmCrudCommand(CrudCommand):
    """Manage specific phylogenetic tree algorithms linked to seqdb implementations and parameters."""

    MODEL_CLASS: ClassVar = model.TreeAlgorithm
