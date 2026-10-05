"""Check sequence sample upload result discriminators."""

import pytest

from gen_epix.etl.model import Result
from gen_epix.seqdb.domain.model.seq.upload import (
    SampleBatchUploadResult,
    SampleUploadResult,
)


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (SampleUploadResult, "d8f4cd68"),
        (SampleBatchUploadResult, "0205001b"),
    ],
    ids=["sample", "sample-batch"],
)
def test_result_id_is_registered_for_polymorphic_deserialization(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "RESULT_ID" not in result_class.model_fields
