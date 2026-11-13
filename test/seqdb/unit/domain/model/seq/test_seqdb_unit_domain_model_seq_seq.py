from typing import Any
from uuid import uuid4

import pytest

from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.model.seq.seq import Seq


def convert(ref_seq: str, **nextclade_fields: str | int) -> str:
    return Seq.get_nucleotide_seq_from_nextclade_format(ref_seq, nextclade_fields)


class TestNextcladeSequenceConversion:
    def test_empty_nextclade_data_returns_reference_sequence(self) -> None:
        assert convert("ACGTACGT") == "ACGTACGT"

    def test_substitutions_support_single_multiple_and_boundary_positions(self) -> None:
        assert convert("acgtacgt", substitutions="A1T,C2G,G3A,T4C,T8A") == "tgacacga"

    def test_substitution_notation_is_case_insensitive_and_mutations_are_lowercase(
        self,
    ) -> None:
        assert convert("acgt", substitutions="A1T,C2G") == "tggt"

    def test_substitution_reference_mismatch_reports_position_and_bases(self) -> None:
        with pytest.raises(ValueError, match="position 2: A provided, found C"):
            convert("AAGT", substitutions="C2G")

    @pytest.mark.parametrize(
        ("non_acgtns", "expected"),
        [
            ("R:2", "ArGTAC"),
            ("Y:2-4", "AyyyAC"),
            ("N:1,X:6", "nCGTAx"),
        ],
    )
    def test_non_acgtns_support_single_ranges_and_multiple_ranges(
        self, non_acgtns: str, expected: str
    ) -> None:
        assert convert("ACGTAC", non_acgtns=non_acgtns) == expected

    @pytest.mark.parametrize(
        ("missings", "expected"),
        [
            ("2", "AnGTAC"),
            ("2-4", "AnnnAC"),
            ("1,3-4,6", "nCn nAn".replace(" ", "")),
        ],
    )
    def test_missing_support_single_ranges_and_multiple_ranges(
        self, missings: str, expected: str
    ) -> None:
        assert convert("ACGTAC", missings=missings) == expected

    @pytest.mark.parametrize(
        ("deletions", "expected"),
        [
            ("2", "AGTAC"),
            ("2-4", "AAC"),
            ("1,3-4,6", "CA"),
        ],
    )
    def test_deletions_remove_single_ranges_and_multiple_ranges(
        self, deletions: str, expected: str
    ) -> None:
        assert convert("ACGTAC", deletions=deletions) == expected

    def test_insertions_support_multiple_symbols_multiple_entries_and_lowercase(
        self,
    ) -> None:
        assert convert("ACGTAC", insertions="2:GGG,5:TA") == "ACgggGTAtaC"

    @pytest.mark.parametrize(
        ("alignment_start", "expected"),
        [("2", "CGTAC"), ("6", "C")],
    )
    def test_alignment_start_removes_prefix_through_boundary(
        self, alignment_start: str, expected: str
    ) -> None:
        assert convert("ACGTAC", alignment_start=alignment_start) == expected

    @pytest.mark.parametrize(
        ("alignment_end", "expected"),
        [("5", "ACGTA"), ("1", "A")],
    )
    def test_alignment_end_removes_suffix_through_boundary(
        self, alignment_end: str, expected: str
    ) -> None:
        assert convert("ACGTAC", alignment_end=alignment_end) == expected

    def test_combined_operations_follow_nextclade_processing_order(self) -> None:
        result = convert(
            "acgtacgtac",
            substitutions="A1T,G3C",
            non_acgtns="R:4-5",
            missings="6",
            deletions="7",
            insertions="8:GG",
            alignment_start=2,
            alignment_end=9,
        )

        assert result == "ccrrntgga"

    def test_combined_operations_preserve_insertions_at_alignment_boundaries(
        self,
    ) -> None:
        result = convert(
            "acgtac",
            substitutions="A1T,T4G",
            insertions="2:TT,5:AA",
            alignment_start=2,
            alignment_end=5,
        )

        assert result == "cttggaaa"


"""
Unit tests for IDSDB ETL model classes.

Tests the Identifier, AlleleForUpload, AlleleProfileForUpload,
and SampleBatchForUpload models with various validation scenarios.
"""


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelSeq:
    """Test cases for Seq model functionality and inheritance."""

    @staticmethod
    def _create_valid_contig() -> model.Contig:
        """Create a valid Contig for testing."""
        return model.Contig(seq="ATCGATCG")

    @staticmethod
    def _create_sample_seq(**kwargs: Any) -> model.Seq:
        """Create a sample Seq with default values and optional overrides."""
        defaults = {
            "sample_id": uuid4(),
            "code": f"seq_{uuid4().hex[:8]}",
            "contigs": [TestModelSeq._create_valid_contig()],
        }
        defaults.update(kwargs)
        return model.Seq(**defaults)  # type: ignore[arg-type]

    def test_seq_creation_with_contigs(self) -> None:
        """Test creating Seq with contigs."""
        contigs = [self._create_valid_contig(), model.Contig(seq="GCTAGCTA")]
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=contigs  # type: ignore[call-arg]
        )
        assert len(seq.contigs) == 2
        assert seq.code == "test_seq"
        assert seq.is_available

    def test_seq_without_contigs(self) -> None:
        """Test creating Seq without contigs (not available)."""
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=[]  # type: ignore[call-arg]
        )
        assert len(seq.contigs) == 0
        assert not seq.is_available

    def test_sample_mixin_inheritance(self) -> None:
        """Test that Seq inherits HasSampleMixin properties."""
        sample_id = uuid4()
        seq = self._create_sample_seq(sample_id=sample_id)
        assert seq.sample_id == sample_id

    def test_code_mixin_inheritance(self) -> None:
        """Test that Seq inherits CodeMixin properties."""
        code = "custom_seq_code"
        seq = self._create_sample_seq(code=code)
        assert seq.code == code

    def test_quality_mixin_inheritance(self) -> None:
        """Test that Seq inherits QualityMixin properties."""
        qc_score = 0.95
        qc_result = model.enum.QualityControlResult.PASS
        seq = self._create_sample_seq(qc_score=qc_score, qc_result_machine=qc_result)
        assert seq.qc_score == qc_score
        assert seq.qc_result == qc_result

    def test_computed_contig_lengths(self) -> None:
        """Test computed fields for contig lengths."""
        short_contig = model.Contig(seq="ATCG")
        long_contig = model.Contig(seq="ATCGATCGATCGATCG")
        seq = model.Seq(
            sample_id=uuid4(),  # type: ignore[call-arg]
            code="test_seq",  # type: ignore[call-arg]
            contigs=[short_contig, long_contig],
        )
        assert seq.min_contig_length == 4
        assert seq.max_contig_length == 16

    def test_empty_contigs_computed_lengths(self) -> None:
        """Test computed lengths with empty contigs list."""
        seq = model.Seq(
            sample_id=uuid4(), code="test_seq", contigs=[]  # type: ignore[call-arg]
        )
        assert seq.min_contig_length == 0
        assert seq.max_contig_length == 0

    def test_assembly_protocol_link(self) -> None:
        """Test assembly protocol relationship."""
        protocol_id = uuid4()
        seq = self._create_sample_seq(protocol_id=protocol_id)
        assert seq.protocol_id == protocol_id

    def test_file_and_read_set_relationships(self) -> None:
        """Test file and read set relationships."""
        file_id = uuid4()
        read_set_id = uuid4()
        read_set2_id = uuid4()

        seq = self._create_sample_seq(
            file_id=file_id,
            file_format=model.enum.SeqFileFormat.FASTA,
            read_set_id=read_set_id,
            read_set2_id=read_set2_id,
        )
        assert seq.file_id == file_id
        assert seq.read_set_id == read_set_id
        assert seq.read_set2_id == read_set2_id

    def test_uri_field(self) -> None:
        """Test URI field functionality."""
        uri = "https://example.com/seq/123"
        seq = self._create_sample_seq(uri=uri)
        assert seq.uri == uri

    def test_contigs_serialization(self) -> None:
        """Test that contigs field exists and has proper structure."""
        seq = self._create_sample_seq()
        # Check that contigs field exists and is a list of Contig objects
        assert isinstance(seq.contigs, list)
        assert len(seq.contigs) > 0
        for contig in seq.contigs:
            assert isinstance(contig, model.Contig)
