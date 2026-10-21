"""Check case upload result discriminator registration."""

import pytest

from gen_epix.casedb.domain.model.case.upload import (
    CaseBatchUploadResult,
    CaseUploadResult,
)
from gen_epix.etl.model import Result


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (CaseUploadResult, "c4fdab13"),
        (CaseBatchUploadResult, "3bb22119"),
    ],
    ids=["case", "case-batch"],
)
def test_result_id_is_registered_for_polymorphic_deserialization(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "RESULT_ID" not in result_class.model_fields
