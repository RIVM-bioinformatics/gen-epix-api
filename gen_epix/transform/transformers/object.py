"""Object transformer implementation."""

from collections.abc import Callable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ObjectTransformer(Transformer):
    """Transform entire object using a custom function."""

    def __init__(self, transform_fn: Callable[[Any], Any], name: str | None = None):
        """Store the callable that transforms the unwrapped object."""
        super().__init__(name)
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the entire object."""
        original = obj.unwrap()
        transformed = self.transform_fn(original)
        return ObjectAdapter(transformed)
