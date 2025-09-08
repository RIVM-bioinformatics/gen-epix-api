from collections.abc import Hashable
from typing import Any


class TupleMap:
    """
    Maps tuples of values from source columns to target columns.
    """

    def __init__(
        self,
        map_rows: list[dict[Hashable, Any]],
        src_column_names: list[Hashable],
        tgt_column_names: list[Hashable],
        map_column_names: list[Hashable],
        is_active_map_column_name: Hashable | None = None,
    ) -> None:
        # Verify input
        if len(set(src_column_names)) < len(src_column_names):
            raise ValueError("Source column names must be unique")
        if len(set(tgt_column_names)) < len(tgt_column_names):
            raise ValueError("Target column names must be unique")
        if len(set(map_column_names)) < len(map_column_names):
            raise ValueError("Map column names must be unique")
        self._src_column_names = src_column_names
        self._tgt_column_names = tgt_column_names
        self._map_column_names = map_column_names
        self._all_column_names = src_column_names + tgt_column_names + map_column_names
        if len(set(self._all_column_names)) < len(self._all_column_names):
            raise ValueError("All column names together must be unique")
        self._is_active_map_column_name = is_active_map_column_name
        self._map_df: list[dict[Hashable, Any]] = map_rows
        self._map: dict[tuple, tuple] = {}

        # Parse map_df into map
        for row in map_rows:
            map_key = tuple(row.get(col) for col in self._map_column_names)
            if map_key in self._map:
                raise ValueError(f"Duplicate mapping for map key {map_key}")
            if self._is_active_map_column_name is not None and not row.get(
                self._is_active_map_column_name, True
            ):
                # Skip inactive mapping
                continue
            map_value = tuple(row.get(col) for col in self._tgt_column_names)
            self._map[map_key] = map_value

    def transform_row(self, row: dict[Hashable, Any]) -> bool:
        return self.transform_rows([row])[0]

    def transform_rows(self, rows: list[dict[Hashable, Any]]) -> list[bool]:
        n_rows = len(rows)
        is_mapped = [False] * n_rows
        for i, row in enumerate(rows):
            key = tuple(row.get(col) for col in self._src_column_names)
            if key not in self._map:
                # No mapping found
                continue
            is_mapped[i] = True
            values = self._map[key]
            for column_name, value in zip(self._tgt_column_names, values):
                rows[i][column_name] = value
        return is_mapped
