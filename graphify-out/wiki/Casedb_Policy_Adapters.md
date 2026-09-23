# Casedb Policy Adapters

> 34 nodes · cohesion 0.06

## Key Concepts

- **casedb/policies/__init__.py** (18 connections) — `gen_epix/casedb/policies/__init__.py`
- **CaseAbacPolicy** (8 connections) — `gen_epix/casedb/policies/case_abac_policy.py`
- **BaseHasSystemOutagePolicy** (8 connections) — `gen_epix/commondb/domain/policy/system.py`
- **HasSystemOutagePolicy** (8 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **ReadOrganizationResultsOnlyPolicy** (5 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **ReadSelfResultsOnlyPolicy** (5 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- **casedb/policies/read_organization_results_only_policy.py** (4 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **.__init__()** (4 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **casedb/policies/read_self_results_only_policy.py** (4 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- **.__init__()** (4 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- **.__init__()** (4 connections) — `gen_epix/commondb/domain/policy/system.py`
- **.get_is_denied_exception()** (3 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **BaseCaseAbacPolicy** (1 connections)
- **Apply command-scoped casedb case access resolution.** (1 connections) — `gen_epix/casedb/policies/case_abac_policy.py`
- **Expose casedb policy adapters and shared policy substitutions. Casedb exports…** (1 connections) — `gen_epix/casedb/policies/__init__.py`
- **Any** (1 connections)
- **BaseAbacService** (1 connections)
- **CommonReadOrganizationResultsOnlyPolicy** (1 connections)
- **Extend organization-scoped result filtering to casedb case policies.** (1 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **Filter casedb case-policy reads to visible organizations.** (1 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **Register casedb case-policy commands for organization filtering. Args:…** (1 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **Any** (1 connections)
- **BaseAbacService** (1 connections)
- **CommonReadSelfResultsOnlyPolicy** (1 connections)
- **Extend self-only result filtering to casedb user case policies.** (1 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- *... and 9 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (10 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (7 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (2 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (2 shared connections)
- [Command Authorization Checks](Command_Authorization_Checks.md) (2 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)
- [Organization Admin Policies](Organization_Admin_Policies.md) (1 shared connections)
- [User Update ABAC Policy](User_Update_ABAC_Policy.md) (1 shared connections)
- [Commondb ABAC Policies](Commondb_ABAC_Policies.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/policies/__init__.py`
- `gen_epix/casedb/policies/case_abac_policy.py`
- `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- `gen_epix/casedb/policies/read_self_results_only_policy.py`
- `gen_epix/commondb/domain/policy/system.py`
- `gen_epix/commondb/policies/has_system_outage_policy.py`

## Audit Trail

- EXTRACTED: 60 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*