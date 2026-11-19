"""Verify OMOP domain enumeration members."""

from gen_epix.omopdb.domain.enum import AnonMethod


def test_model_anonymization_member() -> None:
    """Expose the correctly spelled model anonymization member."""
    assert AnonMethod.MODEL_ANONYMIZATION.name == "MODEL_ANONYMIZATION"
    assert AnonMethod.MODEL_ANONYMIZATION.value == "model_anonymization"
