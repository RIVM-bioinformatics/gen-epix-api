"""
Field transformer implementation.
"""

from collections.abc import Hashable
from typing import Any, Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class FieldTransformer(Transformer):
    """Transform a specific field in an object."""

    def __init__(
        self,
        field_name: Hashable,
        transform_fn: Callable[[Any], Any],
        name: str | None = None,
    ):
        super().__init__(name)
        self.field_name = field_name
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the specified field if it exists."""
        if obj.has_key(self.field_name):
            current_value = obj.get(self.field_name)
            transformed_value = self.transform_fn(current_value)
            obj.set(self.field_name, transformed_value)
        return obj
