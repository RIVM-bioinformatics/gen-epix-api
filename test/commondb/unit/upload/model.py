from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

import gen_epix.fastapp.model
from gen_epix import fastapp
from gen_epix.commondb.domain import command as commondb_command
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.service import BaseService


class Ref1(commondb_model.Model):
    ENTITY: ClassVar = Entity(persistable=True)
    NAME: ClassVar = "Ref1"
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Ref2(commondb_model.Model):
    ENTITY: ClassVar = Entity(persistable=True)
    NAME: ClassVar = "Ref2"
    code: str = Field(description="A unique code")
    a: str = Field(
        default="",
        description="A single value that can always be mutated after first storage.",
    )


class Parent(fastapp.Model):
    ENTITY: ClassVar = Entity(persistable=True, id_field_name="parent_id")
    NAME: ClassVar = "Parent"
    parent_id: UUID | None = Field(
        default=None, description="The ID of the parent model."
    )
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


class ParentIdentifier(commondb_model.BaseIdentifier):
    ENTITY: ClassVar = commondb_model.BaseIdentifier.model_entity().clone()
    NAME: ClassVar = "ParentIdentifier"
    MODEL_CLASS: ClassVar = Parent


class Child1(fastapp.Model):
    ENTITY: ClassVar = Entity(persistable=True, id_field_name="child1_id")
    NAME: ClassVar = "Child1"
    child1_id: UUID | None = Field(
        default=None, description="The ID of the child model."
    )
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


class Child2(fastapp.Model):
    ENTITY: ClassVar = Entity(persistable=True, id_field_name="child2_id")
    NAME: ClassVar = "Child2"
    child2_id: UUID | None = Field(
        default=None, description="The ID of the child model."
    )
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


class Child2Identifier(commondb_model.BaseIdentifier):
    ENTITY: ClassVar = commondb_model.BaseIdentifier.model_entity().clone()
    NAME: ClassVar = "Child2Identifier"
    MODEL_CLASS: ClassVar = Child2


class Child1ForUpload(Child1):
    ENTITY: ClassVar = Child1.model_entity().clone(update={"persistable": False})
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


class Child2ForUpload(Child2, commondb_model.IdentifiersMixin):
    ENTITY: ClassVar = Child2.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "Child2ForUpload"
    IDENTIFIER_CLASS: ClassVar = Child2Identifier

    parent_id: UUID = Field(
        default=NULL_ID,
        description="The ID of the parent model, if available. Otherwise put the null ID.",
    )
    ref2_code: str | None = Field(
        default=None,
        description="The code of the Ref2 model, if available. Otherwise put None.",
    )


class ParentForUpload(commondb_model.ParentForUpload):
    ENTITY: ClassVar = commondb_model.ParentForUpload.model_entity().clone()
    NAME: ClassVar = "ParentForUpload"
    IDENTIFIER_CLASS: ClassVar = ParentIdentifier
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


class Child1UploadResult(commondb_model.UploadResult):
    """Result for uploading a single Child1 object."""

    ENTITY: ClassVar = commondb_model.UploadResult.model_entity().clone()
    NAME: ClassVar = "Child1UploadResult"


class ParentUploadResult(commondb_model.ParentUploadResult):
    ENTITY: ClassVar = commondb_model.ParentUploadResult.model_entity().clone()
    NAME: ClassVar = "ParentUploadResult"
    PARENT_FOR_UPLOAD_CLASS: ClassVar = ParentForUpload  # type: ignore[assignment]

    identifiers: list[UploadResult] | None = Field(
        default=None, description="List of external ID upload results."
    )
    children1: list[UploadResult] | None = Field(
        default=None, description="List of Child1 upload results."
    )
    children2: list[UploadResult] | None = Field(
        default=None, description="List of Child2 upload results."
    )


class ParentBatchForUpload(commondb_model.BaseBatchForUpload):
    ENTITY: ClassVar = commondb_model.BaseBatchForUpload.model_entity().clone()
    NAME: ClassVar = "ParentBatchForUpload"
    PARENT_FOR_UPLOAD_CLASS: ClassVar = ParentForUpload  # type: ignore[assignment]
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "parents"

    parents: list[ParentForUpload] = Field(
        default_factory=list, description="List of Parent models to be uploaded."
    )


class ParentBatchUploadResult(commondb_model.BaseBatchUploadResult):
    ENTITY: ClassVar = commondb_model.BaseBatchUploadResult.model_entity().clone()
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
        user = cmd.user
        parents = cmd.parent_batch.parents
        parent_results = retval.parents

        # Create parent-result pairs
        parent_result_pairs = list(zip(parents, parent_results))

        # Verify all Child1.ref1_id
        success &= self.verify_link_id(
            parent_result_pairs,
            uow,
            user,
            "children1",
            "ref1_id",
            "ref1_code",
            Ref1,
            is_same_service=True,
            is_frozen=False,
        )

        # Verify all Child2.ref2_id
        success &= self.verify_link_id(
            parent_result_pairs,
            uow,
            user,
            "children2",
            "ref2_id",
            "ref2_code",
            Ref2,
            is_same_service=False,
            is_frozen=False,
        )

        return success


# Set model class in entities
for model_class in [
    Parent,
    ParentIdentifier,
    Child1,
    Child2,
    Child2Identifier,
    Child1ForUpload,
    Child2ForUpload,
    ParentForUpload,
]:
    model_class.ENTITY.set_model_class(model_class)
