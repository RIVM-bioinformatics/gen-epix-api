from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.casedb.domain.model.case.operational_data import Case
from gen_epix.casedb.domain.model.seqdb import ReadSet as ReadSet
from gen_epix.casedb.domain.model.seqdb import Seq as Seq
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.util import copy_model_field


class ReadSetForUpload(Model):
    ENTITY: ClassVar = Entity(persistable=False)

    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the read set is or will be associated with."
    )
    sample_id: UUID | None = Field(
        description="The ID of the sample. If provided, the sample must already exist. Must be provided if external_sample_id is not provided.",
        default=None,
    )
    external_sample_id: ExternalIdentifierForUpload | None = Field(
        description="The external identifier of the sample. Used only if sample_id is not provided. Must be provided if sample_id is not provided.",
        default=None,
    )
    read_set_id: UUID | None = Field(
        description="The ID of the read set.", default=None
    )
    read_set: ReadSet | None = Field(default=None, description="The read set.")

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Validate that either sample_id or external_sample_id is provided.
        """
        if self.sample_id is None and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        return self


class SeqForUpload(Model):
    ENTITY: ClassVar = Entity(persistable=False)

    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the sequence is or will be associated with."
    )
    sample_id: UUID | None = Field(
        description="The ID of the sample. If provided, the sample must already exist. Must be provided if external_sample_id is not provided.",
        default=None,
    )
    external_sample_id: ExternalIdentifierForUpload | None = Field(
        description="The external identifier of the sample. Used only if sample_id is not provided. Must be provided if sample_id is not provided.",
        default=None,
    )
    seq_id: UUID | None = Field(description="The ID of the sequence.", default=None)
    seq: Seq | None = Field(default=None, description="The sequence.")

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Validate that either sample_id or external_sample_id is provided.
        """
        if self.sample_id is None and self.external_sample_id is None:
            raise ValueError("Either sample_id or external_sample_id must be provided.")
        return self


class CaseForUpload(Model):
    """
    A class representing a case to be created or updated.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cases_for_create_update",
        persistable=False,
    )
    subject_id: UUID | None = copy_model_field(Case, "subject_id")
    count: int | None = copy_model_field(Case, "count")
    case_date: datetime | None = Field(
        description="The date of the case. Required when creating a case, ignored when updating.",
        default=None,
    )
    content: dict[UUID, str | None] = Field(
        description="The column data of the case as {col_id: str_value}. If None and the model is used for update, then any existing value will be deleted."
    )

    @field_serializer("content", mode="plain")
    def _serialize_content(
        self, value: dict[UUID, str | None]
    ) -> dict[str, str | None]:
        return {str(x): y for x, y in value.items()}
