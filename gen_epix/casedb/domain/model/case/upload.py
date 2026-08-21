from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    SerializerFunctionWrapHandler,
    computed_field,
    field_serializer,
    model_validator,
)

from gen_epix.casedb.domain.model.case.case_data import Case, CaseIdentifier
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import EtlLogItem, Model
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    DataIssue,
    IdentifiersMixin,
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
    by another identifier (other_sample_identifier). The ID of created read set is
    intended to be added to the corresponding case in casedb as the content of the
    given Col.
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    case_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the case that the read set is associated with. If not available, the null ID is put.",
    )
    col_id: UUID = Field(
        description="The ID of the column with column type genetic reads that the read set is or will be associated with."
    )
    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample in seqdb that the read set is associated with. If not available, the null ID is put. Must be provided if other_sample_identifier is not provided.",
    )
    other_sample_identifier: IdentifierForUpload | None = Field(
        default=None,
        description="Another identifier of the sample in seqdb that the read set is associated with. If not available, None is put. Must be provided if sample_id is not provided.",
    )
    protocol_id: UUID = copy_model_field(seqdb_model.ReadSetForUpload, "protocol_id")
    protocol_code: str | None = copy_model_field(
        seqdb_model.ReadSetForUpload, "protocol_code"
    )

    @model_validator(mode="after")
    def _validate_read_set_for_upload(self) -> Self:
        """Validate sample ID and sequencing protocol."""
        if self.sample_id == NULL_ID and self.other_sample_identifier is None:
            raise ValueError(
                "Either sample_id or other_sample_identifier must be provided."
            )
        if not self.protocol_code and self.protocol_id == NULL_ID:
            raise ValueError("Either protocol_code or protocol_id must be provided.")
        return self

    @field_serializer("id", "case_id", "col_id", "sample_id", "protocol_id")
    def _serialize_id(self, value: UUID | None) -> str | None:
        return str(value) if value is not None else None


class SeqForUpload(Model):
    """
    A single sequence to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb.

    The sample can be identified in seqdb either by its internal ID (sample_id) or
    by another identifier (other_sample_identifier). The ID of created sequence is
    intended to be added to the corresponding case in casedb as the content of the
    given Col.
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    case_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the case that the sequence is associated with. If not available, the null ID is put.",
    )
    col_id: UUID = Field(
        description="The ID of the column that the sequence is or will be associated with."
    )
    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample in seqdb that the sequence is associated with. If not available, the null ID is put. Must be provided if other_sample_identifier is not provided.",
    )
    other_sample_identifier: IdentifierForUpload | None = Field(
        default=None,
        description="Another identifier of the sample in seqdb that the sequence is associated with. If not available, None is put. Must be provided if sample_id is not provided.",
    )
    protocol_id: UUID = copy_model_field(seqdb_model.SeqForUpload, "protocol_id")
    protocol_code: str | None = copy_model_field(
        seqdb_model.SeqForUpload, "protocol_code"
    )

    @model_validator(mode="after")
    def _validate_seq_for_upload(self) -> Self:
        """Validate sample ID and assembly protocol."""
        if self.sample_id == NULL_ID and self.other_sample_identifier is None:
            raise ValueError(
                "Either sample_id or other_sample_identifier must be provided."
            )
        if not self.protocol_code and self.protocol_id == NULL_ID:
            raise ValueError("Either protocol_code or protocol_id must be provided.")
        return self

    @field_serializer("id", "case_id", "col_id", "sample_id", "protocol_id")
    def _serialize_id(self, value: UUID | None) -> str | None:
        return str(value) if value is not None else None


class CaseForUpload(ParentForUpload, IdentifiersMixin):
    """
    A case intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = ParentForUpload.model_entity().clone()
    NAME: ClassVar = "CaseForUpload"

    IDENTIFIER_CLASS: ClassVar = CaseIdentifier
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

    @field_serializer("case", mode="wrap")
    def _serialize_case(
        self, value: Case | None, handler: SerializerFunctionWrapHandler
    ) -> Any:
        # Case.content strips None entries on serialization (they mean "no
        # value", not "delete"), which silently discards an upload's intent
        # to delete a content key before it ever reaches the server. Patch
        # the raw, unfiltered content back in for this upload-only wrapper.
        serialized = handler(value)
        if value is not None and serialized is not None:
            serialized["content"] = {
                str(col_id): content_value
                for col_id, content_value in value.content.items()
            }
        return serialized

    # Children
    read_sets: list[ReadSetForUpload] | None = Field(
        default=None,
        description="The read sets to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different Col.",
    )
    seqs: list[SeqForUpload] | None = Field(
        default=None,
        description="The sequences to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different Col.",
    )

    @model_validator(mode="after")
    def _validate_case_for_upload(self) -> Self:
        """
        Verify that read_sets and seqs contain no duplicate col_id, no overlapping
        col_ids across read_sets and seqs, and no inconsistent
        other_sample_identifier to sample ID mappings
        """
        self._validate_read_sets_or_seqs(self.read_sets)
        self._validate_read_sets_or_seqs(self.seqs)
        self._validate_no_col_id_overlap()
        return self

    def _validate_read_sets_or_seqs(
        self, values: list[ReadSetForUpload] | list[SeqForUpload] | None
    ) -> None:
        if values is None:
            return
        if len(values) == 0:
            return
        col_ids = [x.col_id for x in values]
        if len(col_ids) != len(set(col_ids)):
            field_name = (
                "read_sets" if isinstance(values[0], ReadSetForUpload) else "seqs"
            )
            raise ValueError(f"{field_name} must not contain duplicate col_id.")
        sample_id_map: dict[IdentifierForUpload, UUID] = {}
        field_name = "read_sets" if isinstance(values[0], ReadSetForUpload) else "seqs"
        for value in values:
            other_sample_identifier: IdentifierForUpload | None = (
                value.other_sample_identifier
            )
            sample_id = value.sample_id
            if (
                other_sample_identifier is not None
                and sample_id is not None
                and sample_id != NULL_ID
            ):
                # Both provided, check for consistency
                if other_sample_identifier in sample_id_map:
                    if sample_id_map[other_sample_identifier] != sample_id:
                        raise ValueError(
                            f"Inconsistent mapping of other_sample_identifier to sample_id in {field_name}."
                        )
                else:
                    sample_id_map[other_sample_identifier] = sample_id

    def _validate_no_col_id_overlap(self) -> None:
        """Verify that col_ids in read_sets and seqs do not overlap."""
        read_set_col_ids = {x.col_id for x in self.read_sets or []}
        seq_col_ids = {x.col_id for x in self.seqs or []}
        overlap = read_set_col_ids & seq_col_ids
        if overlap:
            overlap_str = ", ".join(str(x) for x in sorted(overlap))
            raise ValueError(
                f"col_id must not appear in both read_sets and seqs. Overlapping col_ids: {overlap_str}"
            )


class CaseDataIssue(DataIssue):
    col_id: UUID = Field(description="The ID of the column")


class CaseUploadResult(ParentUploadResult):
    """
    The result of uploading a single case. The case content validation results as well
    as the resulting cases are included as well.
    """

    ENTITY: ClassVar = ParentUploadResult.model_entity().clone()
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

    identifiers: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the identifiers associated with the case, if any were provided, in the same order as provided.",
    )
    read_sets: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the read sets associated with the case, if any were provided, in the same order as provided.",
    )
    seqs: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequences associated with the case, if any were provided, in the same order as provided.",
    )

    def get_errors(self) -> list[EtlLogItem]:
        """Get all data issues that are errors."""
        log_items = super().get_errors()
        if self.identifiers:
            for identifier_result in self.identifiers:
                log_items.extend(identifier_result.get_errors())
        if self.read_sets:
            for read_set_result in self.read_sets:
                log_items.extend(read_set_result.get_errors())
        if self.seqs:
            for seq_result in self.seqs:
                log_items.extend(seq_result.get_errors())
        return log_items


class CaseBatchForUpload(BaseBatchForUpload):
    """
    A number of unique cases intended for upload.
    """

    ENTITY: ClassVar = BaseBatchForUpload.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "CaseBatchForUpload"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = CaseForUpload
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "cases"

    cases: list[CaseForUpload] = Field(description="The cases to be uploaded.")

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

    def has_samples(self) -> bool:
        """
        Determine if there are any seqdb samples in the cases to be uploaded.
        """
        has_samples = False
        for case_for_upload in self.cases:
            if case_for_upload.read_sets or case_for_upload.seqs:
                has_samples = True
                break
        return has_samples


class CaseBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of cases.
    """

    ENTITY: ClassVar = BaseBatchForUpload.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "CaseBatchUploadResult"

    BATCH_FOR_UPLOAD_CLASS: ClassVar = CaseBatchForUpload
    PARENT_RESULT_CLASS: ClassVar = CaseUploadResult

    cases: list[CaseUploadResult] = Field(
        description="The results of uploading the cases."
    )
