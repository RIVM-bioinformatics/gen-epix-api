# Sequence Distance Calculation

> 52 nodes · cohesion 0.07

## Key Concepts

- **calculate_seq_distance.py** (47 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_and_store_distances()** (28 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **seq_service_update_seq_distances()** (14 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_pairwise_profile_distances()** (11 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_decode_profile()** (11 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_distance_for_decoded_profile_pair()** (10 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **seq_service_retrieve_seq_distance_last_modified()** (8 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_profile_distance()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_parse_nextclade_profile()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_parse_nextclade_profile_content()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_ParsedNextcladeProfile** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_nextclade_snp_hamming_distance()** (6 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_get_matching_seq_profile_protocol_ids()** (6 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **SeqProfileType** (6 connections)
- **_nextclade_hamming_from_parsed()** (5 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_parse_nextclade_non_acgtns()** (5 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_parse_nextclade_ranges()** (5 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_split_nextclade_field()** (5 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **.test_pairwise_reuses_decoded_profiles_no_redecode()** (5 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_parse_nextclade_position_token()** (4 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_parse_nextclade_substitutions()** (4 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **UUID** (4 connections)
- **Implement seqdb sequence service behavior for…** (3 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **_nextclade_position_state()** (3 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **Any** (3 connections)
- *... and 27 more nodes in this community*

## Relationships

- [Allele Hamming Distance Kernels](Allele_Hamming_Distance_Kernels.md) (8 shared connections)
- [Seq Distance Calculation Tests](Seq_Distance_Calculation_Tests.md) (7 shared connections)
- [Numpy Allele Distance Tests](Numpy_Allele_Distance_Tests.md) (6 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (4 shared connections)
- [Seq Distance Update Tests](Seq_Distance_Update_Tests.md) (4 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (4 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (3 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (3 shared connections)
- [Phylogenetic Tree Calculation](Phylogenetic_Tree_Calculation.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 157 (98%)
- INFERRED: 4 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*