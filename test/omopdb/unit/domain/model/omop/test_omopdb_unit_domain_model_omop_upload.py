"""Check OMOP person upload result discriminator registration."""

import pytest

from gen_epix.etl.model import Result
from gen_epix.omopdb.domain.model.omop.upload import (
    PersonBatchUploadResult,
    PersonUploadResult,
)


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (PersonUploadResult, "c6dd271e"),
        (PersonBatchUploadResult, "3d81faf1"),
    ],
    ids=["person", "person-batch"],
)
def test_result_id_is_registered_for_polymorphic_deserialization(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "RESULT_ID" not in result_class.model_fields
