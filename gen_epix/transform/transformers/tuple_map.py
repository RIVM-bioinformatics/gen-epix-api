"""
Tuple map transformer implementation.
"""

from collections.abc import Hashable
from typing import Any

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class TupleMapTransformer(Transformer):
    """
    Maps a tuple of m source fields to a tuple of n target fields using a provided
    mapping. The mapping is provided as a list of dicts, where each dict contains the
    source and target field values for one mapping. The source and target field names
    are specified separately for the rows and the mapping, allowing for flexibility in
    how the mapping is defined and applied. The transformer can also optionally include
    an "is_active" field in the mapping to indicate whether a particular mapping should
    be applied or not.
    """

    def __init__(
        self,
        map_rows: list[dict[Hashable, Any]],
        row_src_fields: list[Hashable],
        row_tgt_fields: list[Hashable],
        map_src_fields: list[Hashable] | None = None,
        map_tgt_fields: list[Hashable] | None = None,
        name: str | None = None,
        is_active_map_field: Hashable | None = None,
    ) -> None:
        """
        Initialise the transformer with the provided mapping and field specifications.
        Args:
            map_rows: A list of dicts, where each dict contains the source and target field values for one mapping.
            row_src_fields: A list of field names for the source fields in the rows to be transformed.
            row_tgt_fields: A list of field names for the target fields in the rows to be transformed.
            map_src_fields: A list of field names for the source fields in the mapping. If None, defaults to row_src_fields.
            map_tgt_fields: A list of field names for the target fields in the mapping. If None, defaults to row_tgt_fields.
            name: An optional name for the transformer.
            is_active_map_field: An optional field name in the mapping that indicates whether a particular mapping should be applied or not. If provided, this field must be a boolean and only mappings with a True value will be applied.
        """
        # Verify input
        n_src_fields = len(row_src_fields)
        if len(set(row_src_fields)) < n_src_fields:
            raise ValueError(
                f"Row source column names are not unique: {row_src_fields}"
            )
        n_tgt_fields = len(row_tgt_fields)
        if len(set(row_tgt_fields)) < n_tgt_fields:
            raise ValueError(
                f"Row target column names are not unique: {row_tgt_fields}"
            )
        row_fields = row_src_fields + row_tgt_fields
        if len(set(row_fields)) < n_src_fields + n_tgt_fields:
            raise ValueError(
                "Row source and target column names together must be unique"
            )
        map_src_fields = map_src_fields or row_src_fields
        map_tgt_fields = map_tgt_fields or row_tgt_fields
        if len(set(map_src_fields)) < len(map_src_fields):
            raise ValueError("Map source column names must be unique")
        if len(map_src_fields) != n_src_fields:
            raise ValueError(
                "Map source columns has different length than row source columns"
            )
        if len(set(map_tgt_fields)) < len(map_tgt_fields):
            raise ValueError("Map target column names must be unique")
        if len(map_tgt_fields) != n_tgt_fields:
            raise ValueError(
                "Map target columns has different length than row target columns"
            )
        map_fields = map_src_fields + map_tgt_fields
        if len(set(map_fields)) < n_src_fields + n_tgt_fields:
            raise ValueError(
                "Map source and target column names together must be unique"
            )
        if is_active_map_field is not None and is_active_map_field in map_fields:
            raise ValueError(
                "is_active_map_field must not be one of the map source or target fields"
            )

        # Initialise some
        super().__init__(name)
        self._n_src_fields = n_src_fields
        self._n_tgt_fields = n_tgt_fields
        self._row_src_fields = row_src_fields
        self._row_tgt_fields = row_tgt_fields
        self._row_fields = row_fields
        self._map_src_fields = map_src_fields
        self._map_tgt_fields = map_tgt_fields
        self._map_fields = map_fields
        self._is_active_map_field = is_active_map_field
        self.update_map(map_rows)

    def update_map(self, map_df: list[dict[Hashable, Any]]) -> None:
        tuple_map: dict[tuple, tuple] = {}
        """
        Update the mapping with the provided mapping dataframe. The mapping dataframe is a list of dicts, where each dict contains the source and target field values for one mapping. The source and target field names in the mapping dataframe are specified by the map_src_fields and map_tgt_fields parameters, respectively. If the is_active_map_field parameter was provided during initialization, only mappings with a True value in that field will be included in the mapping.
        """
        # Extract source and target tuples
        for row in map_df:
            for field in self._map_fields:
                if field not in row:
                    raise KeyError(
                        f"Transformer {self.name}: Missing field {field} in map row: {row}"
                    )
            key = tuple(row[x] for x in self._map_src_fields)
            if key in tuple_map:
                raise KeyError(
                    f"Transformer {self.name}: Duplicate mapping for map field {key}"
                )
            if self._is_active_map_field is not None and not row.get(
                self._is_active_map_field, True
            ):
                # Skip inactive mapping
                continue
            value = tuple(row[x] for x in self._map_tgt_fields)
            tuple_map[key] = value
        self._map_df = map_df
        self._tuple_map = tuple_map

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """
        Transform the provided object using the mapping.

        The object has the target fields added or updated based on the mapping, and is also returned again to allow for method chaining.
        """
        key = tuple(obj.get(x) for x in self._map_src_fields)
        if key not in self._tuple_map:
            raise ValueError(
                f"Transformer {self.name}: Could not find mapping for object: {obj.unwrap()}"
            )
        values = self._tuple_map[key]
        for field, value in zip(self._map_tgt_fields, values):
            obj.set(field, value)
        return obj

    def transform_dict(self, row: dict) -> dict:
        """
        Same as the transform method, but specifically for dicts instead of ObjectAdapters.
        """
        key = tuple(row.get(x) for x in self._map_src_fields)
        if key not in self._tuple_map:
            raise ValueError(
                f"Transformer {self.name}: Could not find mapping for row: {row}"
            )
        values = self._tuple_map[key]
        for field, value in zip(self._map_tgt_fields, values):
            row[field] = value
        return row
