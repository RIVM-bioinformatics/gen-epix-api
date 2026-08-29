"""Transformer for applying independent callables to multiple existing fields."""

from collections.abc import Callable, Hashable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class MultiFieldTransformer(Transformer):
    """Apply configured field callables in mapping order and mutate the adapter."""

    def __init__(
        self,
        field_mapping: dict[Hashable, Callable[[Any], Any]],
        name: str | None = None,
    ):
        """Configure per-field transformation callables."""
        super().__init__(name)
        self.field_mapping = field_mapping

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform each configured field that exists on the adapted object."""
        for field_key, transform_fn in self.field_mapping.items():
            if obj.has_key(field_key):
                old_value = obj.get(field_key)
                new_value = transform_fn(old_value)
                obj.set(field_key, new_value)
        return obj
