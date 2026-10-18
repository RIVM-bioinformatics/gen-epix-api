"""Apply callables to existing fields through the shared adapter interface.

`MultiFieldTransformer` transforms configured fields in mapping order, skips fields
that are absent, and mutates the supplied `ObjectAdapter` in place.
"""

from collections.abc import Callable, Hashable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class MultiFieldTransformer(Transformer):
    """Encapsulates ordered field transformations that mutate an adapter."""

    def __init__(
        self,
        field_mapping: dict[Hashable, Callable[[Any], Any]],
        name: str | None = None,
    ):
        """Configure per-field transformation callables."""
        super().__init__(name)
        self.field_mapping = field_mapping

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform each configured field present on the adapted object.

        Transformations run in mapping order. Missing fields are skipped, and an
        exception from a transformation stops processing and propagates to the
        caller. The adapter is updated in place.

        Args:
            obj: Adapter wrapping the object to transform.

        Returns:
            The same adapter after applying the available transformations.

        Raises:
            Exception: If a configured transformation raises an exception.
        """
        for field_key, transform_fn in self.field_mapping.items():
            if obj.has_key(field_key):
                old_value = obj.get(field_key)
                new_value = transform_fn(old_value)
                obj.set(field_key, new_value)
        return obj
