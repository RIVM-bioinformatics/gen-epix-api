"""Verify dataframe adapter updates are returned by unwrap."""

import polars as pl

from gen_epix.transform.adapter import ObjectAdapter


def test_unwrap_returns_updated_polars_frame() -> None:
    """Expose replacement Polars frames created by adapter updates."""
    original = pl.DataFrame({"value": [1, 2]})
    adapter = ObjectAdapter(original)
    adapter.set("added", [3, 4])

    transformed = adapter.unwrap()

    assert transformed is not original
    assert transformed.columns == ["value", "added"]
    assert transformed["added"].to_list() == [3, 4]
