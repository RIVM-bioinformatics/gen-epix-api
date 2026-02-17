"""
Unit tests for TupleMapTransformer.
"""

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformers.tuple_map import TupleMapTransformer


@pytest.mark.scenario_ids("TC-MAIN-12-01")
class TestTupleMapTransformer:
    """Test cases for TupleMapTransformer."""

    def test_basic_single_field_mapping(self) -> None:
        """Test basic mapping with a single source and single target field."""
        map_rows = [
            {"src": "A", "tgt": 1},
            {"src": "B", "tgt": 2},
            {"src": "C", "tgt": 3},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        test_cases = [
            ({"src": "A"}, 1),
            ({"src": "B"}, 2),
            ({"src": "C"}, 3),
        ]

        for input_dict, expected in test_cases:
            adapter = ObjectAdapter(input_dict)
            result = transformer.transform(adapter)
            assert (
                result.get("tgt") == expected
            ), f"Input {input_dict} should map tgt to {expected}"

    def test_multi_source_to_single_target(self) -> None:
        """Test mapping with multiple source fields to a single target field."""
        map_rows = [
            {"country": "NL", "province": "Noord-Holland", "region": "Randstad"},
            {"country": "NL", "province": "Zuid-Holland", "region": "Randstad"},
            {"country": "BE", "province": "Antwerpen", "region": "Flanders"},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["country", "province"],
            row_tgt_fields=["region"],
        )

        adapter = ObjectAdapter({"country": "NL", "province": "Noord-Holland"})
        result = transformer.transform(adapter)
        assert result.get("region") == "Randstad"

        adapter = ObjectAdapter({"country": "BE", "province": "Antwerpen"})
        result = transformer.transform(adapter)
        assert result.get("region") == "Flanders"

    def test_single_source_to_multi_target(self) -> None:
        """Test mapping with a single source field to multiple target fields."""
        map_rows = [
            {"code": "NL", "country_name": "Netherlands", "continent": "Europe"},
            {
                "code": "US",
                "country_name": "United States",
                "continent": "North America",
            },
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["code"],
            row_tgt_fields=["country_name", "continent"],
        )

        adapter = ObjectAdapter({"code": "NL"})
        result = transformer.transform(adapter)
        assert result.get("country_name") == "Netherlands"
        assert result.get("continent") == "Europe"

        adapter = ObjectAdapter({"code": "US"})
        result = transformer.transform(adapter)
        assert result.get("country_name") == "United States"
        assert result.get("continent") == "North America"

    def test_multi_source_to_multi_target(self) -> None:
        """Test mapping with multiple source and multiple target fields."""
        map_rows = [
            {"src_a": "X", "src_b": 1, "tgt_a": "alpha", "tgt_b": 100},
            {"src_a": "Y", "src_b": 2, "tgt_a": "beta", "tgt_b": 200},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src_a", "src_b"],
            row_tgt_fields=["tgt_a", "tgt_b"],
        )

        adapter = ObjectAdapter({"src_a": "X", "src_b": 1})
        result = transformer.transform(adapter)
        assert result.get("tgt_a") == "alpha"
        assert result.get("tgt_b") == 100

    def test_different_map_and_row_field_names(self) -> None:
        """Test that map_src_fields and map_tgt_fields can differ from row field names.

        The row_src/tgt_fields define uniqueness constraints, while
        map_src/tgt_fields define the actual field names used in the mapping
        and in the objects being transformed.
        """
        map_rows = [
            {"map_code": "A", "map_value": 10},
            {"map_code": "B", "map_value": 20},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["row_code"],
            row_tgt_fields=["row_value"],
            map_src_fields=["map_code"],
            map_tgt_fields=["map_value"],
        )

        # The object must use map field names, since transform() reads/writes using map fields
        adapter = ObjectAdapter({"map_code": "A"})
        result = transformer.transform(adapter)
        assert result.get("map_value") == 10

    def test_is_active_map_field(self) -> None:
        """Test filtering of mappings using is_active_map_field."""
        map_rows = [
            {"src": "A", "tgt": 1, "active": True},
            {"src": "B", "tgt": 2, "active": False},
            {"src": "C", "tgt": 3, "active": True},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
            is_active_map_field="active",
        )

        # "A" is active, should work
        adapter = ObjectAdapter({"src": "A"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 1

        # "B" is inactive, should raise
        adapter = ObjectAdapter({"src": "B"})
        with pytest.raises(ValueError, match="Could not find mapping"):
            transformer.transform(adapter)

        # "C" is active, should work
        adapter = ObjectAdapter({"src": "C"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 3

    def test_transform_no_match_raises(self) -> None:
        """Test that transform raises ValueError when no mapping is found."""
        map_rows = [
            {"src": "A", "tgt": 1},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        adapter = ObjectAdapter({"src": "NONEXISTENT"})
        with pytest.raises(ValueError, match="Could not find mapping"):
            transformer.transform(adapter)

    def test_transform_dict(self) -> None:
        """Test transform_dict for direct dict transformation."""
        map_rows = [
            {"src": "A", "tgt": 1},
            {"src": "B", "tgt": 2},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        row = {"src": "A"}
        result = transformer.transform_dict(row)
        assert result["tgt"] == 1
        assert result is row  # Should mutate and return the same dict

    def test_transform_dict_no_match_raises(self) -> None:
        """Test that transform_dict raises ValueError when no mapping is found."""
        map_rows = [
            {"src": "A", "tgt": 1},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        with pytest.raises(ValueError, match="Could not find mapping"):
            transformer.transform_dict({"src": "MISSING"})

    def test_update_map(self) -> None:
        """Test that update_map replaces the mapping."""
        initial_map = [
            {"src": "A", "tgt": 1},
        ]
        transformer = TupleMapTransformer(
            map_rows=initial_map,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        adapter = ObjectAdapter({"src": "A"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 1

        # Update the map
        new_map = [
            {"src": "A", "tgt": 99},
            {"src": "D", "tgt": 4},
        ]
        transformer.update_map(new_map)

        adapter = ObjectAdapter({"src": "A"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 99

        adapter = ObjectAdapter({"src": "D"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 4

    def test_custom_name(self) -> None:
        """Test that a custom transformer name is used."""
        transformer = TupleMapTransformer(
            map_rows=[{"src": "A", "tgt": 1}],
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
            name="my_custom_mapper",
        )
        assert transformer.name == "my_custom_mapper"

    def test_default_name(self) -> None:
        """Test that the default transformer name is the class name."""
        transformer = TupleMapTransformer(
            map_rows=[{"src": "A", "tgt": 1}],
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )
        assert transformer.name == "TupleMapTransformer"

    def test_preserves_existing_fields(self) -> None:
        """Test that transform preserves existing fields in the object."""
        map_rows = [
            {"src": "A", "tgt": 1},
        ]
        transformer = TupleMapTransformer(
            map_rows=map_rows,
            row_src_fields=["src"],
            row_tgt_fields=["tgt"],
        )

        adapter = ObjectAdapter({"src": "A", "other_field": "keep_me"})
        result = transformer.transform(adapter)
        assert result.get("tgt") == 1
        assert result.get("src") == "A"
        assert result.get("other_field") == "keep_me"


@pytest.mark.scenario_ids("TC-MAIN-12-01")
class TestTupleMapTransformerValidation:
    """Test cases for TupleMapTransformer input validation."""

    def test_duplicate_row_src_fields(self) -> None:
        """Test that duplicate row source field names raise ValueError."""
        with pytest.raises(ValueError, match="Row source column names are not unique"):
            TupleMapTransformer(
                map_rows=[{"a": 1, "tgt": 2}],
                row_src_fields=["a", "a"],
                row_tgt_fields=["tgt"],
            )

    def test_duplicate_row_tgt_fields(self) -> None:
        """Test that duplicate row target field names raise ValueError."""
        with pytest.raises(ValueError, match="Row target column names are not unique"):
            TupleMapTransformer(
                map_rows=[{"src": 1, "a": 2}],
                row_src_fields=["src"],
                row_tgt_fields=["a", "a"],
            )

    def test_overlapping_row_src_and_tgt_fields(self) -> None:
        """Test that overlapping row source and target field names raise ValueError."""
        with pytest.raises(
            ValueError,
            match="Row source and target column names together must be unique",
        ):
            TupleMapTransformer(
                map_rows=[{"x": 1}],
                row_src_fields=["x"],
                row_tgt_fields=["x"],
            )

    def test_map_src_fields_length_mismatch(self) -> None:
        """Test that mismatched map_src_fields length raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Map source columns has different length than row source columns",
        ):
            TupleMapTransformer(
                map_rows=[{"a": 1, "b": 2, "tgt": 3}],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
                map_src_fields=["a", "b"],
            )

    def test_map_tgt_fields_length_mismatch(self) -> None:
        """Test that mismatched map_tgt_fields length raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Map target columns has different length than row target columns",
        ):
            TupleMapTransformer(
                map_rows=[{"src": 1, "a": 2, "b": 3}],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
                map_tgt_fields=["a", "b"],
            )

    def test_duplicate_map_src_fields(self) -> None:
        """Test that duplicate map source field names raise ValueError."""
        with pytest.raises(ValueError, match="Map source column names must be unique"):
            TupleMapTransformer(
                map_rows=[{"a": 1, "tgt": 2}],
                row_src_fields=["src1", "src2"],
                row_tgt_fields=["tgt"],
                map_src_fields=["a", "a"],
            )

    def test_duplicate_map_tgt_fields(self) -> None:
        """Test that duplicate map target field names raise ValueError."""
        with pytest.raises(ValueError, match="Map target column names must be unique"):
            TupleMapTransformer(
                map_rows=[{"src": 1, "a": 2}],
                row_src_fields=["src"],
                row_tgt_fields=["tgt1", "tgt2"],
                map_tgt_fields=["a", "a"],
            )

    def test_overlapping_map_src_and_tgt_fields(self) -> None:
        """Test that overlapping map source and target field names raise ValueError."""
        with pytest.raises(
            ValueError,
            match="Map source and target column names together must be unique",
        ):
            TupleMapTransformer(
                map_rows=[{"x": 1}],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
                map_src_fields=["x"],
                map_tgt_fields=["x"],
            )

    def test_is_active_field_conflicts_with_map_fields(self) -> None:
        """Test that is_active_map_field conflicting with map fields raises ValueError."""
        with pytest.raises(
            ValueError,
            match="is_active_map_field must not be one of the map source or target fields",
        ):
            TupleMapTransformer(
                map_rows=[{"src": 1, "tgt": 2}],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
                is_active_map_field="src",
            )

    def test_duplicate_mapping_key_raises(self) -> None:
        """Test that duplicate mapping keys in map_rows raise KeyError."""
        with pytest.raises(KeyError, match="Duplicate mapping"):
            TupleMapTransformer(
                map_rows=[
                    {"src": "A", "tgt": 1},
                    {"src": "A", "tgt": 2},
                ],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
            )

    def test_missing_field_in_map_row_raises(self) -> None:
        """Test that a missing field in a map row raises KeyError."""
        with pytest.raises(KeyError, match="Missing field"):
            TupleMapTransformer(
                map_rows=[
                    {"src": "A"},  # missing "tgt"
                ],
                row_src_fields=["src"],
                row_tgt_fields=["tgt"],
            )
