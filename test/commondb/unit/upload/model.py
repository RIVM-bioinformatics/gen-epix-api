from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import UploadCommandMixin
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult,
    ForUploadMixin,
    UploadResult,
)


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


class ParentForUpload(Parent, ForUploadMixin):
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None, description="External IDs for the Parent model, if any."
    )
    children1: list[Child1] | None = Field(
        default=None,
        description="List of Child1 models associated with the Parent, if any.",
    )
    children2: list[Child2] | None = Field(
        default=None,
        description="List of Child2 models associated with the Parent, if any.",
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


class ParentBatchForUpload(BaseBatchUploadResult):
    parents: list[ParentForUpload] = Field(
        default_factory=list, description="List of Parent models to be uploaded."
    )


class ParentUploadResult(UploadResult):
    CHILD_RESULT_FIELD_NAMES: ClassVar[list[str]] = []
    CHILD_RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = ["children1", "children2"]
    children1: list[UploadResult] = Field(
        default_factory=list, description="List of Child1 upload results."
    )
    children2: list[UploadResult] = Field(
        default_factory=list, description="List of Child2 upload results."
    )


class ParentBatchUploadResult(model.Model):
    batch_id: UUID = Field(description="The ID of the uploaded Parent batch.")
    parents: list[ParentUploadResult] = Field(
        default_factory=list, description="List of Parent upload results."
    )


class UploadParentsCommand(UploadCommandMixin):
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
