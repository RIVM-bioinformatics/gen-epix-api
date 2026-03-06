from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, field_serializer, model_validator

from gen_epix.casedb.domain.model.case.operational_data import Case
from gen_epix.commondb.domain.enum import IdentifierType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    DataIssue,
    ParentForUpload,
    ParentUploadResult,
    UploadResult,
)
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.util import copy_model_field


class ReadSetForUpload(Model):
    """
    A single read set to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb.

    The sample can be identified in seqdb either by its internal ID (sample_id) or
    by an external identifier (external_sample_id). The ID of created read set is
    intended to be added to the corresponding case in casedb as the content of the
    given case type column.
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    case_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the case that the read set is associated with. If not available, the null ID is put.",
    )
    case_type_col_id: UUID = Field(
        description="The ID of the case type column with column type genetic reads that the read set is or will be associated with."
    )
    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample in seqdb that the read set is associated with. If not available, the null ID is put. Must be provided if external_sample_id is not provided.",
    )
    external_sample_id: ExternalIdentifierForUpload | None = Field(
        default=None,
        description="The external identifier of the sample in seqdb that the read set is associated with. If not available, None is put. Must be provided if sample_id is not provided.",
    )
    sequencing_protocol_id: UUID = copy_model_field(
        seqdb_model.ReadSetForUpload, "sequencing_protocol_id"
    )
    sequencing_protocol_code: str | None = copy_model_field(
        seqdb_model.ReadSetForUpload, "sequencing_protocol_code"
    )

    @model_validator(mode="after")
    def _validate_read_set_for_upload(self) -> Self:
        """Validate sample ID and sequencing protocol."""
        if self.sample_id == NULL_ID and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        if not self.sequencing_protocol_code and self.sequencing_protocol_id == NULL_ID:
            raise ValueError(
                "Either sequencing_protocol_code or sequencing_protocol_id must be provided."
            )
        return self

    @field_serializer(
        "id", "case_id", "case_type_col_id", "sample_id", "sequencing_protocol_id"
    )
    def _serialize_id(self, value: UUID | None) -> str | None:
        return str(value) if value is not None else None


class SeqForUpload(Model):
    """
    A single sequence to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb.

    The sample can be identified in seqdb either by its internal ID (sample_id) or
    by an external identifier (external_sample_id). The ID of created sequence is
    intended to be added to the corresponding case in casedb as the content of the
    given case type column.
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    case_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the case that the read set is associated with. If not available, the null ID is put.",
    )
    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the sequence is or will be associated with."
    )
    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample in seqdb that the sequence is associated with. If not available, the null ID is put. Must be provided if external_sample_id is not provided.",
    )
    external_sample_id: ExternalIdentifierForUpload | None = Field(
        default=None,
        description="The external identifier of the sample in seqdb that the sequence is associated with. If not available, None is put. Must be provided if sample_id is not provided.",
    )
    assembly_protocol_id: UUID = copy_model_field(
        seqdb_model.SeqForUpload, "assembly_protocol_id"
    )
    assembly_protocol_code: str | None = copy_model_field(
        seqdb_model.SeqForUpload, "assembly_protocol_code"
    )

    @model_validator(mode="after")
    def _validate_seq_for_upload(self) -> Self:
        """Validate sample ID and assembly protocol."""
        if self.sample_id == NULL_ID and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        if not self.assembly_protocol_code and self.assembly_protocol_id == NULL_ID:
            raise ValueError(
                "Either assembly_protocol_code or assembly_protocol_id must be provided."
            )
        return self

    @field_serializer(
        "id", "case_id", "case_type_col_id", "sample_id", "assembly_protocol_id"
    )
    def _serialize_id(self, value: UUID | None) -> str | None:
        return str(value) if value is not None else None


class CaseForUpload(ParentForUpload):
    """
    A case intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = ParentForUpload.ENTITY.clone()
    NAME: ClassVar = "CaseForUpload"

    EXTERNAL_IDENTIFIER_TYPE: ClassVar = IdentifierType.CASE
    PARENT_CLASS: ClassVar = Case
    PARENT_FIELD_NAME: ClassVar = "case"
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        ReadSetForUpload: "read_sets",
        SeqForUpload: "seqs",
    }
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        ReadSetForUpload: ReadSetForUpload,
        SeqForUpload: SeqForUpload,
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        x: "case_id" for x in CHILD_FOR_UPLOAD_CLASS_MAP.keys()
    }

    # Parent
    case: Case | None = Field(
        default=None,
        description="The case model itself, if to be created or updated as a whole.",
    )

    # Children
    read_sets: list[ReadSetForUpload] | None = Field(
        default=None,
        description="The read sets to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )
    seqs: list[SeqForUpload] | None = Field(
        default=None,
        description="The sequences to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )

    @model_validator(mode="after")
    def _validate_case_for_upload(self) -> Self:
        """
        Verify that read_sets and seqs contain no duplicate case_type_col_id and no
        inconsistent external ID to sample ID mappings
        """
        self._validate_read_sets_or_seqs(self.read_sets)
        self._validate_read_sets_or_seqs(self.seqs)
        return self

    def _validate_read_sets_or_seqs(
        self, values: list[ReadSetForUpload] | list[SeqForUpload] | None
    ) -> None:
        if values is None:
            return
        if len(values) == 0:
            return
        case_type_col_ids = [x.case_type_col_id for x in values]
        if len(case_type_col_ids) != len(set(case_type_col_ids)):
            field_name = (
                "read_sets" if isinstance(values[0], ReadSetForUpload) else "seqs"
            )
            raise ValueError(
                f"{field_name} must not contain duplicate case_type_col_id."
            )
        sample_id_map: dict[ExternalIdentifierForUpload, UUID] = {}
        field_name = "read_sets" if isinstance(values[0], ReadSetForUpload) else "seqs"
        for value in values:
            external_sample_id: ExternalIdentifierForUpload | None = (
                value.external_sample_id
            )
            sample_id = value.sample_id
            if (
                external_sample_id is not None
                and sample_id is not None
                and sample_id != NULL_ID
            ):
                # Both provided, check for consistency
                if external_sample_id in sample_id_map:
                    if sample_id_map[external_sample_id] != sample_id:
                        raise ValueError(
                            f"Inconsistent mapping of external_sample_id to sample_id in {field_name}."
                        )
                else:
                    sample_id_map[external_sample_id] = sample_id


class CaseDataIssue(DataIssue):
    case_type_col_id: UUID = Field(description="The ID of the case type column")


class CaseUploadResult(ParentUploadResult):
    """
    The result of uploading a single case. The case content validation results as well
    as the resulting cases are included as well.
    """

    ENTITY: ClassVar = ParentUploadResult.ENTITY.clone()
    NAME: ClassVar = "CaseUploadResult"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = CaseForUpload

    validated_content: dict[UUID, str | None] = Field(
        default_factory=dict,
        description="The validated content of the case after validation or upload.",
    )
    data_issues: list[CaseDataIssue] = Field(
        default_factory=list,
        description="The data issues found for the original case content.",
    )

    external_identifiers: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the external identifiers associated with the case, if any were provided, in the same order as provided.",
    )
    read_sets: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the read sets associated with the case, if any were provided, in the same order as provided.",
    )
    seqs: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequences associated with the case, if any were provided, in the same order as provided.",
    )


class CaseBatchForUpload(BaseBatchForUpload):
    """
    A number of unique cases intended for upload.
    """

    ENTITY: ClassVar = BaseBatchForUpload.ENTITY.clone(update={"persistable": False})
    NAME: ClassVar = "CaseBatchForUpload"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = CaseForUpload
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "cases"

    cases: list[CaseForUpload] = Field(description="The cases to be uploaded.")

    @model_validator(mode="after")
    def _validate_external_sample_ids(self) -> Self:
        """Verify that cases contains no duplicate external sample identifiers"""
        external_identifier_map: dict[ExternalIdentifierForUpload, int] = {}
        for i, case_for_upload in enumerate(self.cases):
            for (
                children_field_name
            ) in self.PARENT_FOR_UPLOAD_CLASS.CHILDREN_FIELD_NAME_MAP.values():
                children: list[Model] = getattr(case_for_upload, children_field_name)
                if children is None:
                    continue
                for child in children:
                    external_sample_id: ExternalIdentifierForUpload | None = (
                        child.external_sample_id  # type: ignore[attr-defined]
                    )
                    if external_sample_id is None:
                        continue
                    if external_identifier_map.get(external_sample_id, i) != i:
                        raise ValueError(
                            f"Duplicate external sample identifiers found between children of different cases."
                        )
                    external_identifier_map[external_sample_id] = i
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_read_sets(self) -> bool:
        """Indicates whether there are any read sets in the cases."""
        return any(len(x.read_sets or []) > 0 for x in self.cases)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_seqs(self) -> bool:
        """Indicates whether there are any sequences in the cases."""
        return any(len(x.seqs or []) > 0 for x in self.cases)


class CaseBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of cases.
    """

    ENTITY: ClassVar = BaseBatchForUpload.ENTITY.clone(update={"persistable": False})
    NAME: ClassVar = "CaseBatchUploadResult"

    BATCH_FOR_UPLOAD_CLASS: ClassVar = CaseBatchForUpload
    PARENT_RESULT_CLASS: ClassVar = CaseUploadResult

    cases: list[CaseUploadResult] = Field(
        description="The results of uploading the cases."
    )
