# CaseTypeCrudCommand

> 25 nodes

## Key Concepts

- **CaseTypeCrudCommand** (18 connections) — `gen_epix/casedb/domain/command/case.py`
- **crud_case_type.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **case_service_crud_case_type()** (13 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **_crud_case_type_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **TestCasedbModelProcessMetadata** (10 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **_crud_case_type_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **UUID** (4 connections)
- **.test_update_case_type_does_not_accept_arbitrary_modified_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_preserves_created_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_updates_modified_by()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **BaseCaseService** (3 connections)
- **CaseType** (3 connections)
- **.test_create_case_type_stamps_all_metadata()** (2 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **Manage CaseTypes—the structural and default definitions cases must follow.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **CRUD operations for CaseType entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **Handle CRUD operations for CaseType entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **CaseType admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **CaseType user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **created_at, modified_at, and modified_by must all be set by the backend on…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **created_at must not change when a record is updated.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **modified_at supplied in the update payload must be ignored by the backend.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **modified_by must be stamped with the updating user, not the creating user.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`

## Relationships

- [_crud_cascade_delete](_crud_cascade_delete.md) (8 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (8 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (4 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [TestcasedbEdgeCasesRefDataAccess](TestcasedbEdgeCasesRefDataAccess.md) (2 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [Casedb Case Service Domain Interface](Casedb_Case_Service_Domain_Interface.md) (2 shared connections)
- [CaseService](CaseService.md) (2 shared connections)
- [TestCasedbMetadataMasking](TestCasedbMetadataMasking.md) (1 shared connections)
- [Casedb Metadata Integration Tests](Casedb_Metadata_Integration_Tests.md) (1 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_type.py`
- `test/casedb/integration/metadata/test_casedb_metadata.py`

## Audit Trail

- EXTRACTED: 68 (94%)
- INFERRED: 4 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*