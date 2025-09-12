"""
Tuple map transformer implementation.
"""

from collections.abc import Hashable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class TupleMapTransformer(Transformer):
    """
    Maps tuples of values from source keys to target keys.
    """

    def __init__(
        self,
        map_rows: list[dict[Hashable, Any]],
        src_fields: list[Hashable],
        tgt_fields: list[Hashable],
        name: str | None = None,
        map_fields: list[Hashable] | None = None,
        is_active_map_field: Hashable | None = None,
    ) -> None:
        # Verify input
        if len(set(src_fields)) < len(src_fields):
            raise ValueError("Source column names must be unique")
        if len(set(tgt_fields)) < len(tgt_fields):
            raise ValueError("Target column names must be unique")
        map_fields = map_fields or []
        if len(set(map_fields)) < len(map_fields):
            raise ValueError("Map column names must be unique")

        # Initialise some
        super().__init__(name)
        self._src_fields = src_fields
        self._tgt_fields = tgt_fields
        self._map_fields = map_fields
        self._all_fields = src_fields + tgt_fields + map_fields
        if len(set(self._all_fields)) < len(self._all_fields):
            raise ValueError("All column names together must be unique")
        self._is_active_map_field = is_active_map_field

    def update_map(self, map_df: list[dict[Hashable, Any]]) -> None:
        tuple_map: dict[tuple, tuple] = {}
        # Extract source and target tuples
        for row in map_df:
            key = tuple(row.get(x) for x in self._map_fields)
            if key in tuple_map:
                raise ValueError(f"Duplicate mapping for map field {key}")
            if self._is_active_map_field is not None and not row.get(
                self._is_active_map_field, True
            ):
                # Skip inactive mapping
                continue
            value = tuple(row.get(x) for x in self._tgt_fields)
            tuple_map[key] = value
        self._map_df = map_df
        self._tuple_map = tuple_map

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Map a Transform all specified fields."""
        key = tuple(obj.get(x) for x in self._src_fields)
        if key not in self._tuple_map:
            raise ValueError(f"Validation failed for object: {obj.unwrap()}")
        values = self._tuple_map[key]
        for field, value in zip(self._tgt_fields, values):
            obj.set(field, value)
        return obj
