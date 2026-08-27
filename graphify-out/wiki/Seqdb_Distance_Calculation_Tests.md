# Seqdb Distance Calculation Tests

> 156 nodes · cohesion 0.03

## Key Concepts

- **calculate_seq_distance.py** (50 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **test_seqdb_calculate_seq_distance.py** (50 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **seq_service_calculate_seq_distances_for_new_profiles()** (30 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_calculate_and_store_distances()** (28 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_CrudRecorder** (23 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_setup_distance_mocks()** (23 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_crud_side_effect()** (22 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance_protocol_for_locus_set()** (19 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_allele_profile()** (18 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance()** (16 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestCalculateSeqDistancesForNewProfiles** (16 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **CalculateSeqDistancesResult** (14 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **TestNumpyAlleleIntegration** (14 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **seq_service_update_seq_distances()** (13 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **._run_snp_distance()** (12 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_calculate_pairwise_profile_distances()** (11 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_decode_profile()** (11 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **._run_allele_numpy_calc()** (11 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_calculate_distance_for_decoded_profile_pair()** (10 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **UUID** (9 connections)
- **.test_batch_upload_all_inter_batch_pairs_stored_in_both_maps()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_batch_upload_intra_batch_pair_over_threshold_not_stored()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_snp_profiles_updates_existing_and_creates_new_seq_distances()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_encode_to_int32()** (8 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_hamming_allele_numpy_batch()** (8 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- *... and 131 more nodes in this community*

## Relationships

- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (11 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (10 shared connections)
- [Sample Query Retrieval](Sample_Query_Retrieval.md) (8 shared connections)
- [Seqdb Service CRUD Dispatch](Seqdb_Service_CRUD_Dispatch.md) (7 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (7 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (5 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (4 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (4 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (3 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (3 shared connections)

## Source Files

- `gen_epix/fastapp/exc.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/services/remote_app.py`
- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `gen_epix/seqdb/services/seq/service.py`
- `gen_epix/util.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 497 (100%)
- INFERRED: 2 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*