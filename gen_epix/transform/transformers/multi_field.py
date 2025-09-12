"""
Multi-field transformer implementation.
"""

from collections.abc import Hashable
from typing import Any, Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class MultiFieldTransformer(Transformer):
    """Transform multiple fields simultaneously."""

    def __init__(
        self,
        field_mapping: dict[Hashable, Callable[[Any], Any]],
        name: str | None = None,
    ):
        super().__init__(name)
        self.field_mapping = field_mapping

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform all specified fields."""
        for field_key, transform_fn in self.field_mapping.items():
            if obj.has_key(field_key):
                old_value = obj.get(field_key)
                new_value = transform_fn(old_value)
                obj.set(field_key, new_value)
        return obj
