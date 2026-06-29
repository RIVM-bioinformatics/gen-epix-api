"""
Tuple map transformer implementation.
"""

from collections.abc import Hashable
from typing import Any

from gen_epix.fastapp.enum import OnException
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


    # Review LSP-2989 feature changes

    SUPPORT FOR DEFAULT VALUES:

    - When no mapping is found, default values are applied to the target fields if
      on_no_match=OnException.SET_DEFAULT.
    - default_values is part of the transformer configuration and must have the same
      length as row_tgt_fields.
    - When on_no_match=OnException.RAISE (the default), a ValueError is raised
      if no mapping is found.

    CASE INSENSITIVITY:

    - Matching is case-insensitive by default (case_sensitive=False).
    - When case_sensitive=False, string source field values are lowercased before lookup;
      non-string values are unaffected.
    - Normalization is applied during mapping (at set_map and transform time), not at init.
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
        on_no_match: OnException = OnException.RAISE,
        default_values: tuple[Hashable, ...] | None = None,
        case_sensitive: bool = False,
    ) -> None:
        """
        Initialise the transformer with the provided mapping and field specifications.
        Args:
            map_rows: A list of dicts, where each dict contains the source and target
            field values for one mapping.
            row_src_fields: A list of field names for the source fields in the rows to
            be transformed.
            row_tgt_fields: A list of field names for the target fields in the rows to
            be transformed.
            map_src_fields: A list of field names for the source fields in the mapping.
            If None, defaults to row_src_fields.
            map_tgt_fields: A list of field names for the target fields in the mapping.
            If None, defaults to row_tgt_fields.
            name: An optional name for the transformer.
            is_active_map_field: An optional field name in the mapping that indicates
            whether a particular mapping should be applied or not. If provided, this
            field must be a boolean and only mappings with a True value will be applied.
            on_no_match: action when no mapping is found. Defaults to OnException.RAISE.
            default_values: Default values to apply to target fields when no mapping is
            found. Must be provided when on_no_match is OnException.SET_DEFAULT, and
            must have the same length as row_tgt_fields. If None is provided, the
            default will be an all-None tuple of the appropriate length.
            case_sensitive: If False, string source field values are lowercased before
            lookup. Defaults to True.
        """
        super().__init__(name)

        # Verify input
        self._n_src_fields = len(row_src_fields)
        self._n_tgt_fields = len(row_tgt_fields)
        map_src_fields = map_src_fields or row_src_fields
        map_tgt_fields = map_tgt_fields or row_tgt_fields
        self._verify_map_fields(map_src_fields, map_tgt_fields, is_active_map_field)
        self._verify_row_fields(row_src_fields, row_tgt_fields)
        if default_values is None:
            default_values = tuple([None] * self._n_tgt_fields)
        self._verify_default_values(on_no_match, default_values)

        # Initialise some
        self._row_src_fields = row_src_fields
        self._row_tgt_fields = row_tgt_fields
        self._row_fields = row_src_fields + row_tgt_fields
        self._map_src_fields = map_src_fields
        self._map_tgt_fields = map_tgt_fields
        self._map_fields = map_src_fields + map_tgt_fields
        self._is_active_map_field = is_active_map_field
        self._on_no_match = on_no_match
        self._default_values = (
            tuple(default_values) if default_values is not None else None
        )
        self._case_sensitive = case_sensitive
        self.set_map(map_rows)

    def set_map(self, map_df: list[dict[Hashable, Any]]) -> None:
        tuple_map: dict[tuple, tuple] = {}
        """
        Update the mapping with the provided mapping dataframe. The mapping dataframe
        is a list of dicts, where each dict contains the source and target field values
        for one mapping. The source and target field names in the mapping dataframe are
        specified by the map_src_fields and map_tgt_fields parameters, respectively.
        If the is_active_map_field parameter was provided during initialization,
        only mappings with a True value in that field will be included in the mapping.
        """
        # Extract source and target tuples
        for row in map_df:
            for field in self._map_fields:
                if field not in row:
                    raise KeyError(
                        f"Transformer {self.name}: Missing field {field} in map row: {row}"
                    )
            if self._is_active_map_field is not None and not row.get(
                self._is_active_map_field, True
            ):
                # Skip inactive mapping
                continue
            key = self._normalize_key(tuple(row[x] for x in self._map_src_fields))
            value = tuple(row[x] for x in self._map_tgt_fields)
            if key in tuple_map:
                if tuple_map[key] != value:
                    raise KeyError(
                        f"Transformer {self.name}: Duplicate mapping for map field {key}"
                    )
            else:
                tuple_map[key] = value
        self._map_df = map_df
        self._tuple_map = tuple_map

    def set_row_fields(
        self, row_src_fields: list[Hashable], row_tgt_fields: list[Hashable]
    ) -> None:
        """
        Update the row source and target fields. This allows for changing the field
        names in the rows to be transformed without having to change the mapping
        itself, as long as the new field names are still present in the mapping.
        """
        self._verify_row_fields(row_src_fields, row_tgt_fields)
        self._row_src_fields = row_src_fields
        self._row_tgt_fields = row_tgt_fields
        self._row_fields = row_src_fields + row_tgt_fields

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """
        Transform the provided object using the mapping.

        The object has the target fields added or updated based on the mapping, and is
        also returned again to allow for method chaining.
        """
        key = self._normalize_key(tuple(obj.get(x) for x in self._row_src_fields))
        if key not in self._tuple_map:
            if self._on_no_match == OnException.RAISE:
                raise ValueError(
                    f"Transformer {self.name}: Could not find mapping for object: {obj.unwrap()}"
                )
            elif self._on_no_match == OnException.SET_DEFAULT:
                values = self._default_values
            else:
                raise ValueError(
                    f"Transformer {self.name}: Invalid on_no_match value: {self._on_no_match.value}"
                )
        else:
            values = self._tuple_map[key]
        for field, value in zip(self._row_tgt_fields, values):  # type: ignore[arg-type]
            obj.set(field, value)
        return obj

    def transform_row(self, row: dict) -> dict:
        """
        Same as the transform method, but specifically for dicts (rows with keyed
        values) instead of ObjectAdapters.
        """
        # The ObjectAdapter already wraps dicts transparently, extra computation is minimal
        self.transform(ObjectAdapter(row))
        return row

    def get_row_key(self, row: dict) -> dict:
        """
        Get the source fields and values from the provided row as a dict. This is useful
        for looking up the mapping key for a given row without having to know the
        specific field names used in the mapping, and can be used for debugging or
        logging purposes.
        """
        return {x: row[x] for x in self._row_src_fields}

    def _normalize_key(self, key: tuple) -> tuple:
        if self._case_sensitive:
            return key
        return tuple(x.lower() if isinstance(x, str) else x for x in key)

    def _verify_default_values(
        self,
        on_no_match: OnException,
        default_values: list | None,
    ) -> None:
        if on_no_match == OnException.SET_DEFAULT:
            if default_values is None:
                raise ValueError(
                    "default_values must be provided when on_no_match is SET_DEFAULT"
                )
            if len(default_values) != self._n_tgt_fields:
                raise ValueError(
                    f"default_values length ({len(default_values)}) must match the "
                    f"number of target fields ({self._n_tgt_fields})"
                )

    def _verify_row_fields(
        self, row_src_fields: list[Hashable], row_tgt_fields: list[Hashable]
    ) -> None:
        n_src_fields = len(row_src_fields)
        if n_src_fields != self._n_src_fields:
            raise ValueError(
                "New row source fields must have the same length as the original row "
                "source fields"
            )
        if len(set(row_src_fields)) < n_src_fields:
            raise ValueError(
                f"Row source column names are not unique: {row_src_fields}"
            )
        n_tgt_fields = len(row_tgt_fields)
        if n_tgt_fields != self._n_tgt_fields:
            raise ValueError(
                "New row target fields must have the same length as the original row "
                "target fields"
            )
        if len(set(row_tgt_fields)) < n_tgt_fields:
            raise ValueError(
                f"Row target column names are not unique: {row_tgt_fields}"
            )
        row_fields = row_src_fields + row_tgt_fields
        if len(set(row_fields)) < n_src_fields + n_tgt_fields:
            raise ValueError(
                "Row source and target column names together must be unique"
            )

    def _verify_map_fields(
        self,
        map_src_fields: list[Hashable],
        map_tgt_fields: list[Hashable],
        is_active_map_field: Hashable | None,
    ) -> None:
        if len(set(map_src_fields)) < len(map_src_fields):
            raise ValueError("Map source column names must be unique")
        if len(map_src_fields) != self._n_src_fields:
            raise ValueError(
                "Map source columns has different length than row source columns"
            )
        if len(set(map_tgt_fields)) < len(map_tgt_fields):
            raise ValueError("Map target column names must be unique")
        if len(map_tgt_fields) != self._n_tgt_fields:
            raise ValueError(
                "Map target columns has different length than row target columns"
            )
        map_fields = map_src_fields + map_tgt_fields
        if len(set(map_fields)) < self._n_src_fields + self._n_tgt_fields:
            raise ValueError(
                "Map source and target column names together must be unique"
            )
        if is_active_map_field is not None and is_active_map_field in map_fields:
            raise ValueError(
                "is_active_map_field must not be one of the map source or target fields"
            )
