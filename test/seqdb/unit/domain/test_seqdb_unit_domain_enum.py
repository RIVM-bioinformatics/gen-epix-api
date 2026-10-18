"""Unit tests for sequence-domain enums and factories."""

import datetime
import uuid

import pytest
from pydantic import TypeAdapter

from gen_epix.seqdb.domain.enum import (
    DnaAmbiguityMap,
    DnaReverseAmbiguityMap,
    IdFactory,
    QualityControlResult,
    SeqFormat,
    SeqFormatSet,
    TimestampFactory,
)


@pytest.mark.parametrize(
    ("result", "usable", "sort_key"),
    [
        (QualityControlResult.PENDING, False, 1),
        (QualityControlResult.FAIL, False, 2),
        (QualityControlResult.WARN, True, 3),
        (QualityControlResult.PASS, True, 4),
    ],
    ids=["pending", "fail", "warn", "pass"],
)
def test_quality_control_result_behavior(
    result: QualityControlResult, usable: bool, sort_key: int
) -> None:
    """Report usability and order according to QC severity."""
    assert result.is_usable() is usable
    assert result.get_sort_key() == sort_key


def test_reverse_ambiguity_map_matches_forward_map() -> None:
    """Map each nucleotide to every IUPAC code that includes it."""
    for nucleotide in "acgt":
        expected = frozenset(
            code.lower()
            for code, bases in DnaAmbiguityMap.__members__.items()
            if nucleotide in bases.value
        )
        assert DnaReverseAmbiguityMap[nucleotide.upper()].value == expected


def test_sequence_format_groups() -> None:
    """Group sequence formats by string representation and gap support."""
    assert SeqFormatSet.DNA_AS_STR.value == frozenset(
        {
            SeqFormat.STR_DNA,
            SeqFormat.STR_DNA_INCL_GAP,
            SeqFormat.STR_DNA_GZB64,
            SeqFormat.STR_DNA_INCL_GAP_GZB64,
        }
    )
    assert SeqFormatSet.GAP.value == frozenset(
        {SeqFormat.STR_DNA_INCL_GAP, SeqFormat.STR_DNA_INCL_GAP_GZB64}
    )


def test_enum_json_schema_includes_member_names() -> None:
    """Expose enum names alongside numeric values in generated schemas."""
    schema = TypeAdapter(SeqFormat).json_schema()

    assert schema["x-enum-varnames"] == [member.name for member in SeqFormat]


def test_identifier_factories_return_uuids() -> None:
    """Generate UUID4 and ULID identifiers in UUID form."""
    uuid4_value = IdFactory.UUID4()
    ulid_value = IdFactory.ULID()

    assert isinstance(uuid4_value, uuid.UUID)
    assert uuid4_value.version == 4
    assert isinstance(ulid_value, uuid.UUID)


def test_timestamp_factory_returns_utc_datetime() -> None:
    """Generate timezone-aware timestamps in UTC."""
    timestamp = TimestampFactory.DATETIME_NOW()

    assert isinstance(timestamp, datetime.datetime)
    assert timestamp.tzinfo is datetime.timezone.utc
