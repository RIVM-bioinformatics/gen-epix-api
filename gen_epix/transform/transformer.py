from collections.abc import Hashable
from typing import Any

from gen_epix.transform.tuple_map import TupleMap


class BaseTransformer:

    def __init__(self) -> None:
        self._tuple_maps: dict[Hashable, TupleMap] = {}

    def add_tuple_map(
        self, name: Hashable, tuple_map: TupleMap, replace: bool = False
    ) -> None:
        if name in self._tuple_maps and not replace:
            raise ValueError(f"TupleMap with key {name} already exists")
        self._tuple_maps[name] = tuple_map

    def map_tuple(
        self, tuple_map_name: Hashable, rows: list[dict[Hashable, Any]]
    ) -> list[bool]:
        if tuple_map_name not in self._tuple_maps:
            raise ValueError(f"TupleMap with key {tuple_map_name} does not exist")
        return self._tuple_maps[tuple_map_name].transform_rows(rows)

    def convert_time_resolution(self, rows: list[dict[Hashable, Any]]) -> list[bool]:
        for row in rows:
            # Implement your time resolution conversion logic here
            pass
        return [True] * len(rows)
