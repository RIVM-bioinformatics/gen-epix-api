"""Transformer for replacing an entire adapted object with a callable result."""

from collections.abc import Callable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ObjectTransformer(Transformer):
    """Encapsulates transformation and adaptation of an unwrapped object."""

    def __init__(self, transform_fn: Callable[[Any], Any], name: str | None = None):
        """Store the callable that transforms the unwrapped object."""
        super().__init__(name)
        self.transform_fn = transform_fn

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Return an adapter around the callable's replacement object."""
        original = obj.unwrap()
        transformed = self.transform_fn(original)
        return ObjectAdapter(transformed)
