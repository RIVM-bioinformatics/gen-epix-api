from collections.abc import Hashable
from typing import ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.casedb.domain.model.case.operational_data import Case
from gen_epix.casedb.domain.model.seqdb import AssemblyProtocol as AssemblyProtocol
from gen_epix.casedb.domain.model.seqdb import ReadSet as ReadSet
from gen_epix.casedb.domain.model.seqdb import Sample
from gen_epix.casedb.domain.model.seqdb import Seq as Seq
from gen_epix.casedb.domain.model.seqdb import SequencingProtocol as SequencingProtocol
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    UploadResult,
)
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain.model import ReadSetForUpload as SeqdbReadSetForUpload
from gen_epix.seqdb.domain.model import SeqForUpload as SeqdbSeqForUpload
from gen_epix.util import copy_model_field


class ReadSetForUpload(SeqdbReadSetForUpload):
    """
    A single read set to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb. Equal to the corresponding
    seqdb model, with an additional case_type_col_id property.

    Description of the seqdb model:
    """

    __doc__ = f"{__doc__}{SeqdbReadSetForUpload.__doc__}"

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "ReadSetForUpload"

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
    sample: Sample | None = copy_model_field(SeqdbSeqForUpload, "sample")
    sequencing_protocol: SequencingProtocol | None = copy_model_field(SeqdbReadSetForUpload, "sequencing_protocol")

    @model_validator(mode="after")
    def _validate_read_set_for_upload(self) -> Self:
        if self.sample_id == NULL_ID and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        return self

    @field_serializer("case_id")
    def _serialize_case_id(self, value: UUID) -> str:
        return str(value)


class SeqForUpload(SeqdbSeqForUpload):
    """
    A single sequence to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb. The sample can be identified
    in seqdb either by its internal ID (sample_id) or by an external identifier
    (external_sample_id). The ID of created sequence is intended to be added to
    the corresponding case in casedb as the content of the given case type column.

    Description of the seqdb model:
    """

    __doc__ = f"{__doc__}{SeqdbSeqForUpload.__doc__}"

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SeqForUpload"

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
    sample: Sample | None = copy_model_field(SeqdbSeqForUpload, "sample")
    assembly_protocol: AssemblyProtocol | None = copy_model_field(SeqdbSeqForUpload, "assembly_protocol")
    read_set: ReadSet | None = copy_model_field(SeqdbSeqForUpload, "read_set")
    read_set2: ReadSet | None = copy_model_field(SeqdbSeqForUpload, "read_set2")

    @model_validator(mode="after")
    def _validate_seq_for_upload(self) -> Self:
        if self.sample_id == NULL_ID and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        return self

    @field_serializer("case_id")
    def _serialize_case_id(self, value: UUID) -> str:
        return str(value)


class CaseForUpload(Case):
    """
    A case intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CaseForUpload"

    FOR_UPLOAD_MODEL_CLASS_MAP: ClassVar[dict[type[Model], type[Model]]] = {
        ReadSet: ReadSetForUpload,
        Seq: SeqForUpload,
    }

    MODEL_RESULT_FIELD_NAME_MAP: ClassVar[dict[type[Model], str]] = {
        ReadSetForUpload: "read_sets",
        SeqForUpload: "seqs",
    }

    # Case level data
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="The external identifiers associated with the case, if available.",
    )
    data_collection_ids: set[UUID] | None = Field(
        default=None,
        description="The data collection IDs that the case should be put in. If None, this element is not taken into consideration during the upload.",
    )

    # Associated data
    has_content: bool = Field(
        default=True,
        description="Indicates whether the case has content to be uploaded, since content is a mandatory field and the distinction can otherwise not be made. If False, content must be empty.",
    )
    read_sets: list[ReadSetForUpload] | None = Field(
        default=None,
        description="The read sets to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )
    seqs: list[SeqForUpload] | None = Field(
        default=None,
        description="The sequences to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )

    @field_validator("external_ids", "data_collection_ids", mode="after")
    def _validate_associated_ids(
        cls, value: list[Hashable] | None
    ) -> list[Hashable] | None:
        if value is None:
            return None
        if len(set(value)) != len(value):
            raise ValueError("Associated IDs must be unique.")
        return value

    @model_validator(mode="after")
    def _validate_case_for_upload(self) -> Self:
        # Verify that external_ids contains no duplicates
        if self.external_ids is not None and len(self.external_ids) != len(
            set(self.external_ids)
        ):
            raise ValueError("external_ids must not contain duplicates.")
        # Verify that has_content is consistent with content
        if not self.has_content and self.content:
            raise ValueError(
                "has_content is False, but content is not empty. Content must be empty."
            )
        # Verify that read_sets contains no duplicate case_type_col_id and no inconsistent external ID to sample ID mappings
        self._validate_read_sets_or_seqs(self.read_sets)
        # Verify that seqs contains no duplicate case_type_col_id and no inconsistent external ID to sample ID mappings
        self._validate_read_sets_or_seqs(self.seqs)
        # Verify that result case_ids are consistent with case id
        case_id = NULL_ID if self.id is None else self.id
        for field_name in self.MODEL_RESULT_FIELD_NAME_MAP.values():
            items = getattr(self, field_name)
            for item in items or []:
                if item.case_id == NULL_ID or item.case_id == case_id:
                    continue
                raise ValueError(
                    f"case_id of {field_name} is not the null ID, while the case id variable is not provided."
                )
        return self

    def _validate_read_sets_or_seqs(
        self, values: list[ReadSetForUpload] | list[SeqForUpload] | None
    ) -> None:
        if values is None or len(values) == 0:
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
        for value in values:
            if value.external_sample_id is not None and value.sample_id != NULL_ID:
                if value.external_sample_id in sample_id_map:
                    if sample_id_map[value.external_sample_id] != value.sample_id:
                        field_name = (
                            "read_sets"
                            if isinstance(values[0], ReadSetForUpload)
                            else "seqs"
                        )
                        raise ValueError(
                            f"Inconsistent mapping of external_sample_id to sample_id in {field_name}."
                        )
                else:
                    sample_id_map[value.external_sample_id] = value.sample_id


class CaseUploadResult(UploadResult):
    """
    The result of uploading a single case.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CaseUploadResult"

    SUB_RESULT_FIELD_NAMES: ClassVar = [
        "case_result",
    ]
    SUB_RESULT_LIST_FIELD_NAMES: ClassVar = [
        "external_id_results",
        "data_collection_id_results",
        "read_set_results",
        "seq_results",
    ]

    case_result: UploadResult | None = Field(
        default=None,
        description="The result of uploading or matching the case itself.",
    )
    external_id_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading or matching the external identifiers associated with the case, if any were provided, in the same order as provided.",
    )
    data_collection_id_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of associating the case with the data collections, if any were provided.",
    )
    read_set_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the read sets associated with the case, if any were provided, in the same order as provided.",
    )
    seq_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequences associated with the case, if any were provided, in the same order as provided.",
    )


class CaseBatchForUpload(BaseBatchForUpload):
    """
    A number of unique cases intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CaseBatchForUpload"

    cases: list[CaseForUpload] = Field(description="The cases to be uploaded.")

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        # Verify that cases contain no duplicate case_ids
        case_ids = [x.id for x in self.cases if x.id is not None]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("cases must not contain duplicate case IDs.")
        # Verify that cases contains no duplicate external_ids
        all_external_ids = []
        for case in self.cases:
            if case.external_ids is not None:
                all_external_ids.extend(case.external_ids)
        if len(all_external_ids) != len(set(all_external_ids)):
            raise ValueError("cases must not contain duplicate external_ids.")
        return self

    @computed_field
    @property
    def has_read_sets(self) -> bool:
        """Indicates whether there are any read sets in the cases."""
        return any(len(x.read_sets or []) > 0 for x in self.cases)

    @computed_field
    @property
    def has_seqs(self) -> bool:
        """Indicates whether there are any sequences in the cases."""
        return any(len(x.seqs or []) > 0 for x in self.cases)


class CaseBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of cases.
    """

    SUB_RESULT_LIST_FIELD_NAMES: ClassVar = [
        "case_results",
    ]

    case_results: list[CaseUploadResult] = Field(
        description="The results of uploading the individual cases, in the same order as provided."
    )
