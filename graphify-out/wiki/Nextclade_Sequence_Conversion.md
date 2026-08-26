# Nextclade Sequence Conversion

> 19 nodes · cohesion 0.20

## Key Concepts

- **convert()** (14 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **TestNextcladeSequenceConversion** (13 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **parametrize** (5 connections)
- **.get_nucleotide_seq_from_nextclade_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **test_get_nucleotide_seq_from_nextclade_format.py** (4 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_alignment_end_removes_suffix_through_boundary()** (3 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_alignment_start_removes_prefix_through_boundary()** (3 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_deletions_remove_single_ranges_and_multiple_ranges()** (3 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_missings_support_single_ranges_and_multiple_ranges()** (3 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_non_acgtns_support_single_ranges_and_multiple_ranges()** (3 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_combined_operations_follow_nextclade_processing_order()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_combined_operations_preserve_insertions_at_alignment_boundaries()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_empty_nextclade_data_returns_reference_sequence()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_insertions_support_multiple_symbols_multiple_entries_and_lowercase()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_substitution_notation_is_case_insensitive_and_mutations_are_lowercase()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_substitution_reference_mismatch_reports_position_and_bases()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **.test_substitutions_support_single_multiple_and_boundary_positions()** (2 connections) — `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`
- **Any** (1 connections)
- **Convert a sequence represented in Nextclade format versus a particular…** (1 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`

## Relationships

- [Seq File Format Validation](Seq_File_Format_Validation.md) (2 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/seq.py`
- `test/seqdb/unit/domain/test_get_nucleotide_seq_from_nextclade_format.py`

## Audit Trail

- EXTRACTED: 37 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*