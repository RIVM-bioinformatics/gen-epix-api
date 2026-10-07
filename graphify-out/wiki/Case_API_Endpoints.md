# Case API Endpoints

> 52 nodes · cohesion 0.06

## Key Concepts

- **handle_exception()** (59 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **create_case_endpoints()** (36 connections) — `gen_epix/casedb/api/case.py`
- **create_seq_endpoints()** (26 connections) — `gen_epix/seqdb/api/seq.py`
- **ref_col__validation_rules__get()** (3 connections) — `gen_epix/casedb/api/case.py`
- **case_type_sets__put__case_types()** (2 connections) — `gen_epix/casedb/api/case.py`
- **col_sets__put__cols()** (2 connections) — `gen_epix/casedb/api/case.py`
- **complete_case_types__get_one()** (2 connections) — `gen_epix/casedb/api/case.py`
- **create__case_set()** (2 connections) — `gen_epix/casedb/api/case.py`
- **create_file_for_read_set()** (2 connections) — `gen_epix/casedb/api/case.py`
- **create_file_for_seq()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__assembly_protocols()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_cohort_links_by_case_type()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_ids_by_query()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_rights()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_set_rights()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_set_stats()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__case_type_stats()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__cases_by_ids()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__genetic_sequence_fasta()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__is_own_cases()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__phylogenetic_tree()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__sequencing_protocols()** (2 connections) — `gen_epix/casedb/api/case.py`
- **retrieve__similar_cases()** (2 connections) — `gen_epix/casedb/api/case.py`
- **update__case_created_in_data_collection()** (2 connections) — `gen_epix/casedb/api/case.py`
- **upload__cases()** (2 connections) — `gen_epix/casedb/api/case.py`
- *... and 27 more nodes in this community*

## Relationships

- [Organization & User Endpoints](Organization_&_User_Endpoints.md) (12 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (6 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (4 shared connections)
- [OMOP Endpoints](OMOP_Endpoints.md) (4 shared connections)
- [Casedb Case API Models](Casedb_Case_API_Models.md) (3 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [Seqdb API Request Bodies](Seqdb_API_Request_Bodies.md) (2 shared connections)
- [Authentication Service Base](Authentication_Service_Base.md) (1 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/api/case.py`
- `gen_epix/seqdb/api/seq.py`
- `test/fastapp/integration/api/test_fastapp_api.py`

## Audit Trail

- EXTRACTED: 63 (51%)
- INFERRED: 61 (49%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*