"""Verify transformers return adapter-updated dataframe objects."""

import polars as pl

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transformer import Transformer


class AddColumnTransformer(Transformer):
    """Add a column to the adapted input frame."""

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        obj.set("added", [3, 4])
        return obj


def test_call_returns_transformed_polars_frame() -> None:
    """Expose dataframe updates in the successful transform result."""
    original = pl.DataFrame({"value": [1, 2]})

    result = AddColumnTransformer()(original)

    assert result.success is True
    assert result.transformed_object is not original
    assert result.transformed_object["added"].to_list() == [3, 4]
