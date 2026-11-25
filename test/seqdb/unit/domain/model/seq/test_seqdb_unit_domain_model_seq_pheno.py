"""Verify distinct content format enums for AST and PCR measurements."""

from uuid import uuid4

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement


def test_ast_measurement_uses_ast_result_format() -> None:
    """Normalize AST format values to the AST-specific enum."""
    measurement = AstMeasurement(
        sample_id=uuid4(),
        protocol_id=uuid4(),
        format=1,
        content_hash=uuid4(),
        content="{}",
    )

    assert measurement.format is enum.AstResultFormat.AST_RESULT_FORMAT1


def test_pcr_measurement_uses_pcr_result_format() -> None:
    """Keep PCR format values bound to the PCR-specific enum."""
    measurement = PcrMeasurement(
        sample_id=uuid4(),
        protocol_id=uuid4(),
        format=1,
        content_hash=uuid4(),
        content="{}",
    )

    assert measurement.format is enum.PcrResultFormat.PCR_RESULT_FORMAT1
