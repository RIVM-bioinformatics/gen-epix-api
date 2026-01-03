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
from gen_epix.commondb.services.upload import (
    create_children,
    create_parents,
    update_children,
    update_parents,
    verify_child_existence,
    verify_external_ids,
    verify_link_id,
    verify_parent_existence,
)
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
    FOR_UPLOAD_CHILD_MODEL_CLASS_MAP: ClassVar[
        dict[type[model.Model], type[ForUploadMixin]]
    ] = {
        Child1: Child1ForUpload,
        Child2: Child2ForUpload,
    }
    CHILD_MODEL_FIELD_NAME_MAP: ClassVar[dict[type[ForUploadMixin], str]] = {
        Child1ForUpload: "children1",
        Child2ForUpload: "children2",
    }
    c: dict[str, str | None] = Field(
        description="A dict with values that can be None as well to indicate removal of keys.",
    )
    z: dict[str, str | None] | None = Field(
        description="An optional dict with values that can be None as well to indicate removal of keys.",
    )
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None, description="External IDs for the Parent model, if any."
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
        "external_ids",
        "children1",
        "children2",
    ]

    external_ids: list[UploadResult] | None = Field(
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


def verify_user_rights(
    service: BaseService,
    cmd: UploadParentsCommand,
) -> None:
    """Verify that the user has rights to upload Parent models."""
    pass


def init_retval(
    cmd: UploadParentsCommand,
) -> ParentBatchUploadResult:
    """Initialize the upload result for the Parent batch upload."""
    # Initialize some
    parent_results = []

    def _create_child_results(objs: list | None) -> list[UploadResult] | None:
        if objs is None:
            return None
        return [UploadResult(id=getattr(x, "id", None)) for x in objs]

    # Create a result for each parent with a child result for each child model
    # TODO: use reflection to reduce boilerplate
    for parent in cmd.parent_batch.parents:
        parent_result = ParentUploadResult(
            external_ids=_create_child_results(parent.external_ids),
            children1=_create_child_results(parent.children1),
            children2=_create_child_results(parent.children2),
        )
        parent_results.append(parent_result)

    return ParentBatchUploadResult(
        batch_id=cmd.parent_batch.id,
        parents=parent_results,
    )


def verify_batch(
    service: BaseService,
    cmd: UploadParentsCommand,
    retval: ParentBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify existence of Parent and Child models in the batch."""
    success = True

    # Verify existence and consistency of external IDs
    success &= verify_external_ids(
        service,
        cmd,
        retval,
        uow,
        Parent,
        ParentForUpload,
        IdentifierType.PERSON,
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )
    # Verify existence of parents by ID
    success &= verify_parent_existence(
        service,
        cmd,
        retval,
        uow,
        Parent,
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )
    # Verify existence and consistency of child models as needed
    success &= verify_child_existence(
        service,
        cmd,
        retval,
        uow,
        ParentForUpload,
        "parent_id",
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )
    # Verify reference data links
    success &= verify_refdata_links(
        service,
        cmd,
        retval,
        uow,
    )

    return success


def upsert_batch(
    service: BaseService,
    cmd: UploadParentsCommand,
    retval: ParentBatchUploadResult,
    uow: Any,
) -> bool:
    """Create or update the Parent and any Child models."""
    success = True

    # Upsert parent data
    success &= create_parents(
        service,
        cmd,
        uow,
        Parent,
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )
    success &= update_parents(
        service,
        cmd,
        uow,
        STORED_MODEL_FIELD_PROPS[Parent],
        Parent,
        parents=cmd.parent_batch.parents,  # type: ignore[arg-type]
        parent_results=retval.parents,  # type: ignore[arg-type]
    )

    # Upsert child data
    success &= create_children(
        service,
        cmd,
        uow,
        ParentForUpload,
        "parent_id",
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )
    success &= update_children(
        service,
        cmd,
        uow,
        STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
        ParentForUpload,
        "parent_id",
        cmd.parent_batch.parents,  # type: ignore[arg-type]
        retval.parents,  # type: ignore[arg-type]
    )

    return success


def verify_refdata_links(
    self: BaseService,
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
    success &= verify_link_id(
        self,
        cmd,
        uow,
        ParentForUpload,
        parents,  # type: ignore[arg-type]
        parent_results,  # type: ignore[arg-type]
        "children1",
        "ref1_id",
        "ref1_code",
        Ref1,
        is_same_service=True,
        is_frozen=False,
    )

    # Verify all Child2.ref2_id
    success &= verify_link_id(
        self,
        cmd,
        uow,
        ParentForUpload,
        parents,  # type: ignore[arg-type]
        parent_results,  # type: ignore[arg-type]
        "children2",
        "ref2_id",
        "ref2_code",
        Ref2,
        is_same_service=False,
        is_frozen=False,
    )

    return success
