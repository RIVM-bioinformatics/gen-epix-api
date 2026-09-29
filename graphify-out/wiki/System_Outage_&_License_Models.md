# System Outage & License Models

> 53 nodes · cohesion 0.04

## Key Concepts

- **SystemService** (24 connections) — `gen_epix/commondb/services/system.py`
- **ModelMetadataPolicy** (12 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **PackageMetadata** (11 connections) — `gen_epix/commondb/domain/model/system.py`
- **RetrieveOutagesCommand** (10 connections) — `gen_epix/commondb/domain/command/system.py`
- **model/system.py** (9 connections) — `gen_epix/commondb/domain/model/system.py`
- **RetrieveLicensesCommand** (7 connections) — `gen_epix/commondb/domain/command/system.py`
- **DeleteAllOperationalDataResult** (7 connections) — `gen_epix/commondb/domain/model/system.py`
- **Outage** (7 connections) — `gen_epix/commondb/domain/model/system.py`
- **._parse_and_get_package_metadata()** (6 connections) — `gen_epix/commondb/services/system.py`
- **.filter()** (5 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **.retrieve_licenses()** (5 connections) — `gen_epix/commondb/services/system.py`
- **.delete_all_operational_data()** (4 connections) — `gen_epix/commondb/domain/service/system.py`
- **.retrieve_licenses()** (4 connections) — `gen_epix/commondb/domain/service/system.py`
- **.retrieve_outages()** (4 connections) — `gen_epix/commondb/domain/service/system.py`
- **.__init__()** (4 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **.mask_models()** (4 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **.delete_all_operational_data()** (4 connections) — `gen_epix/commondb/services/system.py`
- **._extract_homepage_from_project_urls()** (4 connections) — `gen_epix/commondb/services/system.py`
- **.retrieve_outages()** (4 connections) — `gen_epix/commondb/services/system.py`
- **_make_user()** (4 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.retrieve_licenses()** (3 connections) — `gen_epix/commondb/services/client.py`
- **._normalize_project_url_label()** (3 connections) — `gen_epix/commondb/services/system.py`
- **.setup_method()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **Any** (2 connections)
- **Delete all operational data from the system. Args: cmd: Command requesting…** (2 connections) — `gen_epix/commondb/services/system.py`
- *... and 28 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (21 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (5 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (4 shared connections)
- [Audit Timestamp Model Tests](Audit_Timestamp_Model_Tests.md) (4 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (3 shared connections)
- [Commondb Client](Commondb_Client.md) (3 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (3 shared connections)
- [System Commands](System_Commands.md) (2 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/command/system.py`
- `gen_epix/commondb/domain/model/system.py`
- `gen_epix/commondb/domain/service/system.py`
- `gen_epix/commondb/policies/model_metadata_policy.py`
- `gen_epix/commondb/services/client.py`
- `gen_epix/commondb/services/system.py`
- `test/commondb/unit/policies/test_model_process_metadata_policy.py`

## Audit Trail

- EXTRACTED: 111 (93%)
- INFERRED: 8 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*