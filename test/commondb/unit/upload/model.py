from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

import gen_epix.fastapp.model
from gen_epix.commondb.domain import command as commondb_command
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.commondb.domain.enum import IdentifierType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.service import BaseService


class Ref1(commondb_model.Model):
    NAME: ClassVar = "Ref1"
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Ref2(commondb_model.Model):
    NAME: ClassVar = "Ref2"
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Parent(commondb_model.Model):
    NAME: ClassVar = "Parent"
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )
    b: list[str] = Field(
        default_factory=list,
        description="A list value that can always be mutated after first storage.",
    )
    c: dict[str, str | None] = Field(
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
    z: dict[str, str | None] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child1(commondb_model.Model):
    NAME: ClassVar = "Child1"
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
    c: dict[str, str | None] = Field(
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
    z: dict[str, str | None] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child2(commondb_model.Model):
    NAME: ClassVar = "Child2"
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
    c: dict[str, str | None] = Field(
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
    z: dict[str, str | None] | None = Field(
        default=None,
        description="A dict value that can be mutated only if the current value is empty (None).",
    )


class Child1ForUpload(Child1, commondb_model.IsNewIdMixin):
    NAME: ClassVar = "Child1ForUpload"
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


class Child2ForUpload(Child2, commondb_model.IsNewIdMixin):
    NAME: ClassVar = "Child2ForUpload"
    parent_id: UUID = Field(
        default=NULL_ID,
        description="The ID of the parent model, if available. Otherwise put the null ID.",
    )
    ref2_code: str | None = Field(
        default=None,
        description="The code of the Ref2 model, if available. Otherwise put None.",
    )


class ParentForUpload(commondb_model.ParentForUpload):
    NAME: ClassVar = "ParentForUpload"
    PARENT_IDENTIFIER_TYPE: ClassVar[IdentifierType] = IdentifierType.PERSON
    PARENT_CLASS: ClassVar = Parent
    PARENT_FIELD_NAME: ClassVar = "parent"
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        Child1: Child1ForUpload,
        Child2: Child2ForUpload,
    }
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        Child1: "children1",
        Child2: "children2",
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        Child1: "parent_id",
        Child2: "parent_id",
    }

    parent: Parent | None = Field(
        default=None,
        description="The Parent model itself, if to be created or updated as a whole.",
    )
    children1: list[Child1ForUpload] | None = Field(
        default=None,
        description="List of Child1 models associated with the Parent, if any.",
    )
    children2: list[Child2ForUpload] | None = Field(
        default=None,
        description="List of Child2 models associated with the Parent, if any.",
    )


class ParentUploadResult(commondb_model.ParentUploadResult):
    PARENT_FOR_UPLOAD_CLASS: ClassVar = ParentForUpload  # type: ignore[assignment]

    external_identifiers: list[UploadResult] | None = Field(
        default=None, description="List of external ID upload results."
    )
    children1: list[UploadResult] | None = Field(
        default=None, description="List of Child1 upload results."
    )
    children2: list[UploadResult] | None = Field(
        default=None, description="List of Child2 upload results."
    )


class ParentBatchForUpload(commondb_model.BaseBatchForUpload):
    NAME: ClassVar = "ParentBatchForUpload"
    PARENT_FOR_UPLOAD_CLASS: ClassVar = ParentForUpload  # type: ignore[assignment]
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "parents"

    parents: list[ParentForUpload] = Field(
        default_factory=list, description="List of Parent models to be uploaded."
    )


class ParentBatchUploadResult(commondb_model.BaseBatchUploadResult):
    BATCH_FOR_UPLOAD_CLASS: ClassVar = ParentBatchForUpload  # type: ignore[assignment]
    PARENT_RESULT_CLASS: ClassVar = ParentUploadResult

    parents: list[ParentUploadResult] = Field(
        default_factory=list, description="List of Parent upload results."
    )


class UploadParentsCommand(
    commondb_command.Command, commondb_command.UploadBatchCommandMixin
):
    BATCH_FOR_UPLOAD_CLASS: ClassVar = ParentBatchForUpload
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar = "parent_batch"
    BATCH_UPLOAD_RESULT_CLASS: ClassVar = ParentBatchUploadResult

    parent_batch: ParentBatchForUpload = Field(
        description="The batch of Parent models to be uploaded."
    )


STORED_MODEL_FIELD_PROPS = {
    Parent: {
        "a": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "c": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
            is_sub_field_dict=True,
        ),
        "x": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "z": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_sub_field_dict=True,
        ),
    },
    Child1: {
        "a": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "c": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
            is_sub_field_dict=True,
        ),
        "x": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "z": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_sub_field_dict=True,
        ),
    },
    Child2: {
        "a": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "b": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
        ),
        "c": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_always=True,
            is_sub_field_dict=True,
        ),
        "x": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "y": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
        ),
        "z": gen_epix.fastapp.model.ModelFieldProps(
            is_mutable_if_empty=True,
            is_sub_field_dict=True,
        ),
    },
}


class ParentBatchUploader(BatchUploader):
    """Service to handle batch upload of Parent models."""

    def __init__(self, service: BaseService) -> None:
        super().__init__(
            UploadParentsCommand,
            STORED_MODEL_FIELD_PROPS,
            service,
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
