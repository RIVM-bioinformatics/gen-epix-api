"""Tests for sequence representation helpers."""

import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.model.seq.base import (
    decode_ascii_from_gzip_base64,
    encode_ascii_as_gzip_base64,
)


@pytest.mark.parametrize("value", ["", "ACGTN", "line one\nline two"])
def test_gzip_base64_round_trip_is_deterministic(value: str) -> None:
    """Encode ASCII content reproducibly and recover the exact input."""
    encoded = encode_ascii_as_gzip_base64(value)

    assert encode_ascii_as_gzip_base64(value) == encoded
    assert decode_ascii_from_gzip_base64(encoded) == value


@pytest.mark.parametrize("value", ["not base64!", "", "YWJj"])
def test_decode_rejects_invalid_or_non_gzip_payloads(value: str) -> None:
    """Normalize malformed base64 and gzip data to a consistent ValueError."""
    with pytest.raises(ValueError, match="not a valid base64-encoded gzip archive"):
        decode_ascii_from_gzip_base64(value)


"""
Unit tests for IDSDB ETL model classes.

Tests the Identifier, AlleleForUpload, AlleleProfileForUpload,
and SampleBatchForUpload models with various validation scenarios.
"""


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelBaseSeq:
    """Test cases for BaseSeq model validation and functionality."""

    @staticmethod
    def _get_valid_dna_sequence() -> str:
        """Return a valid DNA sequence for testing."""
        return "ATCGATCGATCG"

    @staticmethod
    def _get_invalid_dna_sequence() -> str:
        """Return an invalid DNA sequence for testing."""
        return "ATCGXYZ123"

    @staticmethod
    def _compute_expected_hash(sequence: str) -> UUID:
        """Compute the expected sequence hash for a given sequence."""
        normalized_seq = sequence.lower()
        return UUID(hashlib.sha256(normalized_seq.encode("ascii")).digest()[:16].hex())

    def test_valid_sequence_creation(self) -> None:
        """Test creating BaseSeq with valid DNA sequence."""
        seq = "ATCGATCG"
        base_seq = model.BaseSeq(seq=seq)
        assert base_seq.seq == seq.lower()
        assert base_seq.length == len(seq)
        assert base_seq.seq_format == model.enum.SeqFormat.STR_DNA
        assert base_seq.id is not None

    def test_sequence_normalization(self) -> None:
        """Test that DNA sequences are normalized to lowercase."""
        seq = "ATCGATCG"
        base_seq = model.BaseSeq(seq=seq)
        assert base_seq.seq == seq.lower()

    def test_automatic_length_calculation(self) -> None:
        """Test that length is automatically calculated when set to 0."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq, length=0)
        assert base_seq.length == len(seq)

    def test_explicit_length_validation(self) -> None:
        """Test that explicit length must match sequence length."""
        seq = self._get_valid_dna_sequence()
        # Valid matching length
        base_seq = model.BaseSeq(seq=seq, length=len(seq))
        assert base_seq.length == len(seq)

        # Invalid mismatched length
        with pytest.raises(
            ValidationError, match="Provided length does not match computed length"
        ):
            model.BaseSeq(seq=seq, length=len(seq) + 1)

    def test_hash_calculation(self) -> None:
        """Test that sequence hash is correctly calculated."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq)
        expected_hash = self._compute_expected_hash(seq)
        assert base_seq.id == expected_hash

    def test_explicit_hash_validation(self) -> None:
        """Test that explicit hash must match computed hash."""
        seq = self._get_valid_dna_sequence()
        expected_hash = self._compute_expected_hash(seq)

        # Valid matching hash
        base_seq = model.BaseSeq(seq=seq, id=expected_hash)
        assert base_seq.id == expected_hash

        # Invalid mismatched hash
        with pytest.raises(
            ValidationError, match="does not match computed sequence hash"
        ):
            model.BaseSeq(seq=seq, id=uuid4())

    def test_invalid_dna_characters(self) -> None:
        """Test that invalid DNA characters raise ValidationError."""
        invalid_seq = self._get_invalid_dna_sequence()
        with pytest.raises(ValidationError, match="invalid characters"):
            model.BaseSeq(seq=invalid_seq)

    def test_ambiguous_dna_characters(self) -> None:
        """Test that ambiguous IUPAC DNA characters are allowed."""
        seq_with_ambiguous = "ATCGRYSWKMBDHVN"
        base_seq = model.BaseSeq(seq=seq_with_ambiguous)
        assert base_seq.seq == seq_with_ambiguous.lower()
        assert base_seq.length == len(seq_with_ambiguous)

    def test_empty_sequence_error(self) -> None:
        """Test that empty sequence raises appropriate error."""
        with pytest.raises(
            ValidationError, match="Unable to calculate sequence length"
        ):
            model.BaseSeq(seq="", length=0)

    def test_seq_format_serialization(self) -> None:
        """Test that seq_format is properly serialized."""
        seq = self._get_valid_dna_sequence()
        base_seq = model.BaseSeq(seq=seq)
        serialized = base_seq.model_dump()
        assert serialized["seq_format"] == 2

    def test_different_seq_formats(self) -> None:
        """Test handling of different sequence formats."""
        seq = self._get_valid_dna_sequence()
        # Test with explicit format
        base_seq = model.BaseSeq(seq=seq, seq_format=model.enum.SeqFormat.STR_DNA)
        assert base_seq.seq_format == model.enum.SeqFormat.STR_DNA

        # Test with hash only format (should rely on provided hash)
        custom_hash = uuid4()
        with pytest.raises(
            ValidationError, match="Unable to calculate sequence length"
        ):
            model.BaseSeq(
                seq="custom_format_seq",
                seq_format=model.enum.SeqFormat.HASH_ONLY,
                id=custom_hash,
            )

    def test_hash_only_sequence_with_length(self) -> None:
        """HASH_ONLY format accepts a sequence when length is provided."""
        custom_hash = uuid4()
        base_seq = model.BaseSeq(
            seq="opaque_data",
            seq_format=model.enum.SeqFormat.HASH_ONLY,
            length=42,
            id=custom_hash,
        )
        assert base_seq.id == custom_hash
        assert base_seq.length == 42
        assert base_seq.seq_format == model.enum.SeqFormat.HASH_ONLY
        assert base_seq.seq == "opaque_data"

    @pytest.mark.parametrize(
        ("seq_format", "expected_alphabet"),
        [
            (model.enum.SeqFormat.STR_DNA_INCL_GAP, "acgt-n"),
            (model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64, "acgt-n"),
        ],
    )
    def test_gap_inclusive_sequence_validation(
        self, seq_format: model.enum.SeqFormat, expected_alphabet: str
    ) -> None:
        """Test validation and hashing of gap-inclusive DNA representations."""
        sequence = "AT-GN"
        stored_sequence = (
            encode_ascii_as_gzip_base64(sequence)
            if seq_format == model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64
            else sequence
        )
        base_seq = model.BaseSeq(seq=stored_sequence, seq_format=seq_format)

        assert base_seq.get_nucleotide_seq() == sequence.lower()
        assert base_seq.length == len(sequence)
        assert base_seq.id == self._compute_expected_hash(sequence)
        if seq_format == model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64:
            assert base_seq.seq != sequence.lower()
        else:
            assert set(base_seq.seq) <= set(expected_alphabet)

        with pytest.raises(ValidationError, match="invalid characters"):
            invalid_sequence = (
                encode_ascii_as_gzip_base64("AT-X")
                if seq_format == model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64
                else "AT-X"
            )
            model.BaseSeq(seq=invalid_sequence, seq_format=seq_format)

    @pytest.mark.parametrize(
        "seq_format",
        [
            model.enum.SeqFormat.STR_DNA_GZB64,
            model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64,
        ],
    )
    def test_gzip_base64_sequence_round_trip(
        self, seq_format: model.enum.SeqFormat
    ) -> None:
        """Test gzip+base64 storage while exposing the decoded DNA sequence."""
        sequence = "ATCGATCG"
        if seq_format == model.enum.SeqFormat.STR_DNA_INCL_GAP_GZB64:
            sequence = "AT-CGATCG"

        base_seq = model.BaseSeq(
            seq=encode_ascii_as_gzip_base64(sequence), seq_format=seq_format
        )

        assert base_seq.seq != sequence.lower()
        assert base_seq.get_nucleotide_seq() == sequence.lower()
        assert base_seq.length == len(sequence)
        assert base_seq.id == self._compute_expected_hash(sequence)

    # def test_gzip_base64_rejects_malformed_storage(self) -> None:
    #     """Reject compressed sequence data that is not valid gzip+base64."""
    #     with pytest.raises(ValidationError, match="valid gzip\+base64"):
    #         model.BaseSeq(
    #             seq="not-valid-gzip-base64",
    #             seq_format=model.enum.SeqFormat.STR_DNA_GZB64,
    #         )

    @pytest.mark.parametrize(
        ("seq_format", "sequence"),
        [
            ("STR_DNA_GZB64", "ATCGATCG"),
            ("STR_DNA_INCL_GAP_GZB64", "AT-CGATCG"),
        ],
    )
    def test_gzip_base64_accepts_plain_sequence(
        self, seq_format: str, sequence: str
    ) -> None:
        """Encode a plain nucleotide string when compressed storage is requested."""
        base_seq = model.BaseSeq(seq=sequence, seq_format=seq_format)  # type: ignore[arg-type]

        assert base_seq.seq == encode_ascii_as_gzip_base64(sequence.lower())
        assert base_seq.get_nucleotide_seq() == sequence.lower()

    def test_gapless_dna_rejects_alignment_gap(self) -> None:
        """Reject alignment gaps when the selected format is gapless DNA."""
        with pytest.raises(ValidationError, match="invalid characters"):
            model.BaseSeq(seq="AT-CG", seq_format=model.enum.SeqFormat.STR_DNA)
