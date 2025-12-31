from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from gen_epix import fastapp


class Model(fastapp.Model):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )


class ModelFieldProps(BaseModel):
    is_mutable_if_empty: bool = Field(
        default=True,
        description="Indicates whether the field is mutable after initial creation in the database if its initial value is empty (None, empty dict, empty list).",
    )
    is_mutable_always: bool = Field(
        default=False,
        description="Indicates whether the field is always mutable after initial creation in the database. Cannot be True if is_mutable_if_empty is False.",
    )
    is_dict: bool = Field(
        default=False,
        description="Indicates whether the field content is a dictionary of values rather than a single value. Cannot be True if is_list is also True.",
    )
    is_list: bool = Field(
        default=False,
        description="Indicates whether the field content is a list of values rather than a single value. Cannot be True if is_dict is also True.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if not self.is_mutable_if_empty and self.is_mutable_always:
            raise ValueError(
                "is_mutable_always cannot be True if is_mutable_if_empty is False."
            )
        if self.is_dict and self.is_list:
            raise ValueError("A field cannot be both a dict and a list.")
        return self

    def is_mutable_value(self, stored_value: Any | None) -> bool:
        """
        Determine if a stored value for this field is mutable.
        """
        if self.is_mutable_always:
            return True
        if self.is_mutable_if_empty:
            if self.is_dict or self.is_list:
                return stored_value is None or len(stored_value) == 0
            if stored_value is None:
                return True
        return False
