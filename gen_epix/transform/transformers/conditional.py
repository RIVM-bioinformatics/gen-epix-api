"""Transformer that conditionally delegates to another transformer."""

from collections.abc import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class ConditionalTransformer(Transformer):
    """Encapsulates predicate-controlled transformation."""

    def __init__(
        self,
        condition: Callable[[ObjectAdapter], bool],
        transformer: Transformer,
        name: str | None = None,
    ):
        """Store the predicate and transformer used for conditional execution."""
        super().__init__(name)
        self.condition = condition
        self.transformer = transformer

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform `obj` when the predicate returns true; otherwise return it unchanged."""
        if self.condition(obj):
            return self.transformer.transform(obj)
        return obj
