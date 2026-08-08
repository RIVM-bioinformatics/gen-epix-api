"""
Unit tests for SeqProfile.nextclade_get_ref_alignment.

Tests cover:
- Basic shape and content of the result DataFrame
- Equivalence of DataFrame and dict inputs
- Behavior of the remove_conserved flag
- Behavior of the uppercase flag
- Behavior when ref_seq is None (remove_conserved mode)
"""

import numpy as np
import pandas as pd

ref_seq = (
    "ACGTACGTAC"  # 1-10
    "GTACGTACGT"  # 11-20
    "ACGTACGTAC"  # 21-30
    "GTACGTACGT"  # 31-40
    "ACGTACGTAC"  # 41-50
    "GTACGTACGT"  # 51-60
    "ACGTACGTAC"  # 61-70
    "GTACGTACGT"  # 71-80
    "ACGTACGTAC"  # 81-90
    "GTACGTACGT"  # 91-100
)
assert len(ref_seq) == 100

data = {
    "seq_name": [
        "sample_clean",  # 0: no differences
        "sample_subs",  # 1: substitutions only
        "sample_del",  # 2: deletions only
        "sample_ins",  # 3: insertions only
        "sample_missing",  # 4: missing data only
        "sample_nonacgtn",  # 5: non-ACGTNs only
        "sample_partial",  # 6: partial alignment
        "sample_combo",  # 7: all event types
    ],
    "substitutions": [
        np.nan,  # 0
        "A1T,C2G,G15A",  # 1: 3 subs
        np.nan,  # 2
        np.nan,  # 3
        np.nan,  # 4
        np.nan,  # 5
        np.nan,  # 6
        "T4C,A5G",  # 7: 2 subs
    ],
    "deletions": [
        np.nan,  # 0
        np.nan,  # 1
        "10-12",  # 2: positions 10,11,12
        np.nan,  # 3
        np.nan,  # 4
        np.nan,  # 5
        np.nan,  # 6
        "20",  # 7: single deletion
    ],
    "insertions": [
        np.nan,  # 0
        np.nan,  # 1
        np.nan,  # 2
        "5:GGG,50:AA",  # 3: two insertions
        np.nan,  # 4
        np.nan,  # 5
        np.nan,  # 6
        "30:TTT",  # 7: one insertion
    ],
    "missings": [
        np.nan,  # 0
        np.nan,  # 1
        np.nan,  # 2
        np.nan,  # 3
        "80-85",  # 4: positions 80..85
        np.nan,  # 5
        np.nan,  # 6
        "90-92",  # 7: positions 90..92
    ],
    "non_acgtns": [
        np.nan,  # 0
        np.nan,  # 1
        np.nan,  # 2
        np.nan,  # 3
        np.nan,  # 4
        "R:30-31",  # 5: ambiguity R at 30,31
        np.nan,  # 6
        "Y:60",  # 7: ambiguity Y at 60
    ],
    "alignment_start": [
        1,
        1,
        1,
        1,
        1,
        1,
        10,  # 6: starts at pos 10
        1,
    ],
    "alignment_end": [
        100,
        100,
        100,
        100,
        100,
        100,
        90,  # 6: ends at pos 90
        100,
    ],
}

nextclade_df = pd.DataFrame(data)

# TODO: Uncomment if nextclade_get_ref_alignment is used in the code
# @pytest.mark.scenario_ids("TC-SEC-29-03")
# class TestNextcladeGetRefAlignment:
#     """Tests for SeqProfile.nextclade_get_ref_alignment."""

#     def test_basic_shape_and_content(self) -> None:
#         result = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=ref_seq,
#             remove_conserved=False,
#             uppercase=True,
#             verify=False,
#         )
#         # --- Basic shape checks ---
#         assert result.shape[0] == 8, f"Expected 8 rows, got {result.shape[0]}"
#         # At least 100 columns (reference positions)
#         # plus insertion columns
#         assert result.shape[1] >= 100, f"Expected >=100 cols, got {result.shape[1]}"
#         # --- Check sample_clean: all reference letters ---
#         clean = result.loc["sample_clean"]
#         assert clean["A1"] == "A"
#         assert clean["C2"] == "C"
#         assert clean["G3"] == "G"
#         assert clean["T4"] == "T"
#         assert clean["C10"] == "C"

#     def test_dict_input_equals_dataframe_input(self) -> None:
#         result = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=ref_seq,
#             remove_conserved=False,
#             uppercase=True,
#             verify=False,
#         )
#         nextclade_df_dict: dict[str, dict[str, Any]] = (
#             nextclade_df.set_index("seqName")
#             .drop(columns=[""], errors="ignore")  # removes the empty index column
#             .to_dict(orient="index")
#         )
#         result_dict = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df_dict,
#             ref_seq=ref_seq,
#             remove_conserved=False,
#             uppercase=True,
#             verify=False,
#         )
#         assert result.equals(result_dict)

#     def test_remove_conserved_produces_fewer_columns(self) -> None:
#         result = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=ref_seq,
#             remove_conserved=False,
#             uppercase=True,
#             verify=False,
#         )
#         result_rc = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=ref_seq,
#             remove_conserved=True,
#             uppercase=True,
#             verify=False,
#         )
#         # Should have fewer columns (only polymorphic ones)
#         assert (
#             result_rc.shape[1] < result.shape[1]
#         ), "remove_conserved should produce fewer columns"
#         # Substitution columns should still be present
#         assert "A1" in result_rc.columns
#         assert "C2" in result_rc.columns

#     def test_uppercase_false_lowercases_bases(self) -> None:
#         result_lc = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=ref_seq,
#             remove_conserved=False,
#             uppercase=False,
#             verify=False,
#         )
#         lc_clean = result_lc.loc["sample_clean"]
#         assert lc_clean["A1"] == "a"
#         assert lc_clean["C2"] == "c"

#     def test_no_ref_seq_remove_conserved(self) -> None:
#         result_noref = model.SeqProfile.nextclade_get_ref_alignment(
#             nextclade_df,
#             ref_seq=None,
#             remove_conserved=True,
#             uppercase=True,
#             verify=False,
#         )
#         # Should only contain polymorphic columns
#         assert result_noref.shape[1] < 100
