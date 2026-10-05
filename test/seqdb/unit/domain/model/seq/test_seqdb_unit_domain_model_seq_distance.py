"""Check the sequence-distance ETL result discriminator."""

from gen_epix.etl.model import Result
from gen_epix.seqdb.domain.model.seq.distance import CalculateSeqDistancesEtlResult


def test_result_id_is_registered_for_polymorphic_deserialization() -> None:
    result_class = CalculateSeqDistancesEtlResult

    assert result_class.RESULT_ID == "6e359c57"
    assert Result._SUBCLASS_REGISTRY[result_class.RESULT_ID] is result_class
    assert "RESULT_ID" not in result_class.model_fields
