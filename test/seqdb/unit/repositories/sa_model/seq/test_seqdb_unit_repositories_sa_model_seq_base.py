"""Test SQLAlchemy mappings for shared seqdb sequence columns."""

import sqlalchemy as sa
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.repositories.sa_model.seq import Allele, AstMeasurement


def test_content_mixin_maps_required_and_optional_columns() -> None:
    """Map content fields with their storage types and nullability."""
    columns = AstMeasurement.__table__.c

    assert isinstance(columns.format.type, sa.Integer)
    assert isinstance(columns.content_hash.type, UUIDType)
    assert isinstance(columns.content.type, sa.Text)
    assert columns.content.nullable is False
    assert isinstance(columns.content2.type, sa.Text)
    assert columns.content2.nullable is True


def test_quality_mixin_maps_quality_columns() -> None:
    """Map quality results, scores, and optional JSON reports."""
    columns = AstMeasurement.__table__.c

    assert isinstance(columns.qc_result_machine.type, sa.String)
    assert isinstance(columns.qc_result_human.type, sa.String)
    assert isinstance(columns.qc_score.type, sa.Float)
    assert isinstance(columns.qc_report.type, sa.JSON)
    assert columns.qc_report.nullable is True


def test_seq_mixin_maps_sequence_columns() -> None:
    """Map sequence text, format, and length fields."""
    columns = Allele.__table__.c

    assert isinstance(columns.seq.type, sa.Text)
    assert columns.seq.nullable is False
    assert isinstance(columns.seq_format.type, sa.Enum)
    assert columns.seq_format.type.enum_class is seqdb_enum.SeqFormat
    assert isinstance(columns.length.type, sa.Integer)
