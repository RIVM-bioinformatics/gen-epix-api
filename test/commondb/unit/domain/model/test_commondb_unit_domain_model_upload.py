"""Check upload result identifiers and model fields."""

import pytest

from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult,
    ParentUploadResult,
    UploadResult,
    UploadResultWithIdentifiers,
)
from gen_epix.etl.model import Result


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (UploadResult, "c4f1a9e2"),
        (UploadResultWithIdentifiers, "06e14d51"),
        (ParentUploadResult, "f354e913"),
        (BaseBatchUploadResult, "6d64fbc3"),
    ],
    ids=["upload", "with-identifiers", "parent", "batch"],
)
def test_result_id_is_registered_and_object_id_remains_a_field(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "id" in result_class.model_fields
    assert "RESULT_ID" not in result_class.model_fields
