import pytest

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
    def test_missings_support_single_ranges_and_multiple_ranges(
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
