# Case Operational Data Models

> 43 nodes · cohesion 0.09

## Key Concepts

- **ops_data.py** (24 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **Case** (20 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **TestModelCaseOpsData** (14 connections) — `test/casedb/unit/domain/model/case/test_casedb_model_case_ops_data.py`
- **CaseDataCollectionLink** (11 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **case_service_calculate_case_date()** (11 connections) — `gen_epix/casedb/services/case/case_date.py`
- **CaseIdentifier** (9 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **test_casedb_model_case_ops_data.py** (9 connections) — `test/casedb/unit/domain/model/case/test_casedb_model_case_ops_data.py`
- **CaseSet** (7 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **CaseSetDataCollectionLink** (7 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **CaseSetMember** (7 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **convert_iso_date_to_datetime()** (7 connections) — `gen_epix/casedb/services/case/case_date.py`
- **test_casedb_get_case_date.py** (7 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **TestGetCaseDate** (7 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **convert_iso_week_to_first_day_datetime()** (6 connections) — `gen_epix/casedb/services/case/case_date.py`
- **Model** (5 connections)
- **._make_case()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **.test_falls_back_to_lower_resolution_when_higher_is_none()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **.test_stops_at_highest_resolution_when_both_day_and_week_present()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **._serialize_cohort()** (4 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **._serialize_content()** (4 connections) — `gen_epix/casedb/domain/model/case/ops_data.py`
- **.test_all_cols_none_leaves_case_date_unchanged()** (4 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **UUID** (3 connections)
- **.test_case_identifier_instantiation()** (3 connections) — `test/casedb/unit/domain/model/case/test_casedb_model_case_ops_data.py`
- **.test_case_set_member_and_data_collection_link_instantiation()** (3 connections) — `test/casedb/unit/domain/model/case/test_casedb_model_case_ops_data.py`
- **field_serializer** (2 connections)
- *... and 18 more nodes in this community*

## Relationships

- [Complete Case Type Models](Complete_Case_Type_Models.md) (9 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (8 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [Case Validator Tests](Case_Validator_Tests.md) (4 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (2 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (2 shared connections)
- [Test Data Creation Helpers](Test_Data_Creation_Helpers.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/ops_data.py`
- `gen_epix/casedb/services/case/case_date.py`
- `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- `test/casedb/unit/domain/model/case/test_casedb_model_case_ops_data.py`

## Audit Trail

- EXTRACTED: 109 (85%)
- INFERRED: 19 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*