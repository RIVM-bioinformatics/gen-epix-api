from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.domain.command.base import UploadCommandMixin
from gen_epix.commondb.domain.enum import IdentifierType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    ForUploadMixin,
    UploadResult,
)
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.service import BaseService


class Ref1(model.Model):
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Ref2(model.Model):
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Parent(model.Model):
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )
    b: list[str] = Field(
        default_factory=list,
        description="A list value that can always be mutated after first storage.",
    )
    c: dict[str, str] = Field(
        default_factory=dict,
        description="A dict value that can always be mutated after first storage.",
    )
    x: str | None = Field(
        default=None,
        description="A single value that can be mutated only if the current value is empty (None).",
    )
    y: list[str] | None = Field(
        default=None,
        description="A list value that can be mutated only if the current value is empty (None).",
    )
    z: dict[str, str] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child1(model.Model):
    parent_id: UUID = Field(description="The ID of the parent model.")
    ref1_id: UUID = Field(description="The ID of the Ref1 model.")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )
    b: list[str] = Field(
        default_factory=list,
        description="A list value that can always be mutated after first storage.",
    )
    c: dict[str, str] = Field(
        default_factory=dict,
        description="A dict value that can always be mutated after first storage.",
    )
    x: str | None = Field(
        default=None,
        description="A single value that can be mutated only if the current value is empty (None).",
    )
    y: list[str] | None = Field(
        default=None,
        description="A list value that can be mutated only if the current value is empty (None).",
    )
    z: dict[str, str] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child2(model.Model):
    parent_id: UUID = Field(description="The ID of the parent model.")
    ref2_id: UUID | None = Field(description="The ID of the Ref2 model.")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )
    b: list[str] = Field(
        default_factory=list,
        description="A list value that can always be mutated after first storage.",
    )
    c: dict[str, str] = Field(
        default_factory=dict,
        description="A dict value that can always be mutated after first storage.",
    )
    x: str | None = Field(
        default=None,
        description="A single value that can be mutated only if the current value is empty (None).",
    )
    y: list[str] | None = Field(
        default=None,
        description="A list value that can be mutated only if the current value is empty (None).",
    )
    z: dict[str, str] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child1ForUpload(Child1, ForUploadMixin):
    parent_id: UUID = Field(
        default=NULL_ID,
        description="The ID of the parent model, if available. Otherwise put the null ID.",
    )
    ref1_id: UUID = Field(
        default=NULL_ID,
        description="The ID of the Ref1 model, if available. Otherwise put the null ID.",
    )
    ref1_code: str | None = Field(
        default=None,
        description="The code of the Ref1 model, if available. Otherwise put None.",
    )
    c: dict[str, str | None] = Field(
        description="A dict with values that can be None as well to indicate removal of keys.",
    )
    z: dict[str, str | None] | None = Field(
        description="An optional dict with values that can be None as well to indicate removal of keys.",
    )

    @model_validator(mode="after")
    def _validate_ref1_fields(self) -> Self:
        """
        Validate that either ref1_id or ref1_code is provided.
        """
        if self.ref1_id == NULL_ID and not self.ref1_code:
            raise ValueError(
                "Either ref1_id or ref1_code must be provided for Child1ForUpload."
            )
        return self


class Child2ForUpload(Child2, ForUploadMixin):
    parent_id: UUID = Field(
        default=NULL_ID,
        description="The ID of the parent model, if available. Otherwise put the null ID.",
    )
    ref2_code: str | None = Field(
        default=None,
        description="The code of the Ref2 model, if available. Otherwise put None.",
    )
    c: dict[str, str | None] = Field(
        description="A dict with values that can be None as well to indicate removal of keys.",
    )
    z: dict[str, str | None] | None = Field(
        description="An optional dict with values that can be None as well to indicate removal of keys.",
    )


class ParentForUpload(Parent, ForUploadMixin):
    IDENTIFIER_TYPE: ClassVar[IdentifierType] = IdentifierType.PERSON
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar[
        dict[type[model.Model], type[ForUploadMixin]]
    ] = {
        Child1: Child1ForUpload,
        Child2: Child2ForUpload,
    }
    CHILDREN_FIELD_NAME_MAP: ClassVar[dict[type[model.Model], str]] = {
        Child1: "children1",
        Child2: "children2",
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar[dict[type[model.Model], str]] = {
        Child1: "parent_id",
        Child2: "parent_id",
    }
    EXTERNAL_IDENTIFIERS_FIELD_NAME: ClassVar[str] = "external_identifiers"
    c: dict[str, str | None] = Field(
        description="A dict with values that can be None as well to indicate removal of keys.",
    )
    z: dict[str, str | None] | None = Field(
        description="An optional dict with values that can be None as well to indicate removal of keys.",
    )
    external_identifiers: list[ExternalIdentifierForUpload] | None = Field(
        default=None, description="External identifiers for the Parent model, if any."
    )
    children1: list[Child1ForUpload] | None = Field(
        default=None,
        description="List of Child1 models associated with the Parent, if any.",
    )
    children2: list[Child2ForUpload] | None = Field(
        default=None,
        description="List of Child2 models associated with the Parent, if any.",
    )


class ParentBatchForUpload(BaseBatchForUpload):
    parents: list[ParentForUpload] = Field(
        default_factory=list, description="List of Parent models to be uploaded."
    )


class ParentUploadResult(UploadResult):
    CHILD_RESULT_FIELD_NAMES: ClassVar[list[str]] = []
    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = [
        "external_identifiers",
        "children1",
        "children2",
    ]

    external_identifiers: list[UploadResult] | None = Field(
        default=None, description="List of external ID upload results."
    )
    children1: list[UploadResult] | None = Field(
        default=None, description="List of Child1 upload results."
    )
    children2: list[UploadResult] | None = Field(
        default=None, description="List of Child2 upload results."
    )


class ParentBatchUploadResult(BaseBatchUploadResult):
    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = ["parents"]

    parents: list[ParentUploadResult] = Field(
        default_factory=list, description="List of Parent upload results."
    )


class UploadParentsCommand(Command, UploadCommandMixin):
    parent_batch: ParentBatchForUpload = Field(
        description="The batch of Parent models to be uploaded."
    )


STORED_MODEL_FIELD_PROPS = {
    Parent: {
        "a": model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": model.ModelFieldProps(
            is_mutable_always=True,
            is_list=True,
        ),
        "c": model.ModelFieldProps(
            is_mutable_always=True,
            is_dict=True,
        ),
        "x": model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_list=True,
        ),
        "z": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_dict=True,
        ),
    },
    Child1: {
        "a": model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": model.ModelFieldProps(
            is_mutable_always=True,
            is_list=True,
        ),
        "c": model.ModelFieldProps(
            is_mutable_always=True,
            is_dict=True,
        ),
        "x": model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_list=True,
        ),
        "z": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_dict=True,
        ),
    },
    Child2: {
        "a": model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": model.ModelFieldProps(
            is_mutable_always=True,
            is_list=True,
        ),
        "c": model.ModelFieldProps(
            is_mutable_always=True,
            is_dict=True,
        ),
        "x": model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_list=True,
        ),
        "z": model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_dict=True,
        ),
    },
}


class ParentBatchUploader(BatchUploader):
    """Service to handle batch upload of Parent models."""

    def __init__(self, service: BaseService) -> None:
        super().__init__(
            service=service,
            stored_model_field_props=STORED_MODEL_FIELD_PROPS,
            cmd_batch_field_name="parent_batch",
            batch_class=ParentBatchForUpload,
            batch_result_class=ParentBatchUploadResult,
            batch_parents_field_name="parents",
            parent_class=Parent,
            parent_for_upload_class=ParentForUpload,
            parent_result_class=ParentUploadResult,
            external_identifier_model_class=model.ExternalIdentifier,
        )

    def verify_refdata(
        self,
        cmd: UploadParentsCommand,
        retval: ParentBatchUploadResult,
        uow: Any,
    ) -> bool:
        """
        Verify and complete reference data for allele profiles.
        """
        success = True
        user_id = cmd.user.id if cmd.user else None
        parents = cmd.parent_batch.parents
        parent_results = retval.parents

        # Verify all Child1.ref1_id
        success &= self.verify_link_id(
            cmd,
            retval,
            uow,
            "children1",
            "ref1_id",
            "ref1_code",
            Ref1,
            is_same_service=True,
            is_frozen=False,
        )

        # Verify all Child2.ref2_id
        success &= self.verify_link_id(
            cmd,
            retval,
            uow,
            "children2",
            "ref2_id",
            "ref2_code",
            Ref2,
            is_same_service=False,
            is_frozen=False,
        )

        return success
