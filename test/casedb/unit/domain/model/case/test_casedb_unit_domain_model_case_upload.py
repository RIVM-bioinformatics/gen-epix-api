"""Check case upload result discriminator registration."""

from uuid import uuid4

import pytest

from gen_epix.casedb.domain.model.case.upload import (
    CaseBatchUploadResult,
    CaseForUpload,
    CaseUploadResult,
    ReadSetForUpload,
    SeqForUpload,
)
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
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


def test_case_upload_rejects_sample_identifier_mapped_to_different_ids_across_child_types() -> (
    None
):
    other_sample_identifier = IdentifierForUpload(
        identifier_issuer_code="LAB", external_id="sample-1"
    )

    with pytest.raises(
        ValueError, match="Inconsistent mapping of other_sample_identifier"
    ):
        CaseForUpload(
            read_sets=[
                ReadSetForUpload(
                    col_id=uuid4(),
                    sample_id=uuid4(),
                    other_sample_identifier=other_sample_identifier,
                    protocol_id=uuid4(),
                )
            ],
            seqs=[
                SeqForUpload(
                    col_id=uuid4(),
                    sample_id=uuid4(),
                    other_sample_identifier=other_sample_identifier,
                    protocol_id=uuid4(),
                )
            ],
        )
