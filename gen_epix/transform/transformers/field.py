"""Transformer for applying a callable to one field of an adapted object."""

from collections.abc import Callable, Hashable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class FieldTransformer(Transformer):
    """Encapsulates in-place transformation of one existing field."""

    def __init__(
        self,
        field_name: Hashable,
        transform_fn: Callable[[Any], Any],
        name: str | None = None,
    ):
        """Configure the field and callable used for in-place field updates."""
        super().__init__(name)
        self.field_name = field_name
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the field when present, leaving objects without it unchanged."""
        if obj.has_key(self.field_name):
            current_value = obj.get(self.field_name)
            transformed_value = self.transform_fn(current_value)
            obj.set(self.field_name, transformed_value)
        return obj
