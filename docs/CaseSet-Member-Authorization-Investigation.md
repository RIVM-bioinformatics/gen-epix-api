# CaseSetManagementWorkflow authorization investigation

Investigated on 20 October 2026 across the current API and PPR working trees.
Existing unrelated working-tree changes were preserved. No services were restarted,
production records changed, commits created, or load tests launched.

## 1. Root Cause

The immediate HTTP 403 is an API regression in commit `0ea71503` (18 October
2026, PR #790), in
`gen_epix/casedb/services/case/crud_case_set_member.py`. It changed the restricted
handler to reject every `READ_ALL`, even when a query selects explicit case IDs.
The generated `POST /v1/case_set_members/query` endpoint always constructs
`CaseSetMemberCrudCommand(operation=READ_ALL)`. Its filter does not turn it into
`READ_SOME`; that operation expects membership record IDs.

The earlier centralization commit `881589c7` (8 October) changed exemption
dispatch but did not introduce this guard. Before PR #790, the member handler
delegated these reads through a temporary, incompletely authorized CRUD path.
Restoring that delegation would discard the new row-level checks and is not an
appropriate fix.

The investigation also found missing case ABAC policy registration for
`CaseSetMemberCrudCommand`. The command appeared in the exemption map but not in
`BaseAbacService.CASE_ABAC_COMMANDS`. Simply permitting filtered reads would
therefore have reached the old no-metadata delegation branch. The patch registers
the policy and rejects missing metadata for non-exempt membership requests.

There is a separate PPR sharing defect: cases are uploaded with the uploader's
private creation collection, while
`ShareUploadedCasesInDataCollection.run()` had its HTTP request commented out.
Its callers also selected `shared_data_collection_id`, rather than the phase's
national collection. The late sharing calls in CaseSet management attempted to
link other organizations' cases after membership operations had already begun.

## 2. Why It Failed

### Request sequence and permissions

HOT MHS users wait for the PHI upload gate, log in, and claim a chunk of uploaded
case IDs. `create_case_set()` reads categories, statuses, and collections, then
queries memberships by `case_id` **before creating any CaseSet**. That first
query fails at the operation guard, before collection IDs, ownership, case types,
or effective collection permissions are inspected.

The workflow's intended collection selection is:

| Phase | Shared target | Configured default ID |
| --- | --- | --- |
| HOT | `national_event_data_collection_id` | `01918870-0a02-15c2-f48b-5432ab38c754` |
| COLD | `national_surveillance_data_collection_id` | `018d074d-e9fc-5c35-9d3c-4bbdbaf851d2` |

Both CaseSets and cases retain a private creation collection. Shared availability
comes from collection links. Creating a CaseSet directly in a national collection
would conflict with the PDP's private-creation requirement.

Provisioning already creates organization and user access policies for both
national collections. Every generated ORG_USER receives those policies. Effective
rights combine organization and user grants; a user grant alone is insufficient.
National case-column reads, CaseSet reads/writes, and adding CaseSets were already
configured. National organization policies did not allow adding cases.

`Manager` loads reference data before Locust spawns users. The supplied run logs
show 201 organizations, 1,206 users, 804 organization policies, and 4,020 user
policies created by 10:07:40, before uploads begin at 10:08:56. This is not evidence
of a provisioning race.

Membership reads require access to **both** their case and CaseSet. Membership
creation requires case read access, CaseSet write access, and matching case types.
Sharing a case requires case write access and permission to add it to the target
collection. None of these operations follows automatically from knowing a shared
collection ID.

### Log correlation

In `/tmp/ppr_output/logs/load_test_e127c3ec-8b2f-4e44-a6f8-dcc72c2885ac.log`,
the first logged request failure is line 45, at **10:10:36 Europe/Amsterdam**,
for `mhs71`. It precedes the supplied `mhs16` example at 10:10:51 (line 133).

The matching PPR `output/iteration_details.csv` contains 3,004 request records
for this run: 182 membership-query 403s (181 HOT, one COLD), seven statistics
422s, and 2,815 HTTP 200s. There are **zero** CaseSet creation requests, member
insertion requests, or case-collection-link batch requests. The membership
failure prevents the creation workflow from reaching those operations.

The 182 membership errors affect ten MHS users and one PHI user. Both `mhs16`
and `mhs47` occur repeatedly. The supplied API timestamp, 08:11:29 UTC, corresponds
to 10:11:29 locally; the available PPR log does not contain that exact `mhs47`
occurrence. These are distinct requests with the same failure signature, not
evidence of an account mix-up. No request ID in the supplied API entry establishes
a one-to-one match.

The logs omit the membership filter values and record no successful creation, so
they cannot identify the exact case UUIDs or a newly created CaseSet UUID for the
failing request. The private origins and intended targets above are established
from the workflow and configuration code, not recovered request payloads or a
read of the deployed database.

## 3. Implemented Solution

### API

- Register `CaseSetMemberCrudCommand` for the existing DURING-phase case ABAC
  policy. Require its metadata for non-exempt member operations.
- Permit member bulk reads only with a non-inverted UUID-set filter on `case_id`
  or `case_set_id`. Keep filtering by both parent resources' read permissions.
- Authorize member creation using readable cases, writable CaseSets, and matching
  case types. Check the entire batch before persistence.
- Permit collection-link queries only with a non-inverted CaseSet UUID selection;
  keep the existing linked-collection CaseSet read checks.
- Authorize case sharing using source case write access and target `ADD_CASE`
  rights. Check the entire batch before persistence.

These changes stay in services and existing policy registration. Routes, command
contracts, exemption roles, and repository implementations are unchanged.
Unrestricted/inverted membership queries and other unsupported writes remain
rejected. Both collections' content permissions remain enforced.

### PPR

- Restore the existing sharing workflow's request, using the original uploader's
  credentials and the shared request helper.
- Select the national event collection for HOT uploads and the national
  surveillance collection for COLD uploads. Share before publishing uploaded case
  IDs to consumers.
- Grant organization `add_case` only to PHI for the event collection and LAB for
  the surveillance collection. Preserve MHS read-only case access and existing
  national column-write/remove restrictions. User policies already grant the
  corresponding add flag.
- Remove late sharing requests from CaseSet creation and member addition; those
  consumers now operate on cases already shared by their uploader.

A PPR-only permission change cannot fix the unconditional API operation rejection.
Removing the membership queries would hide that incompatibility and would still
leave existing-CaseSet member insertion unsupported. The API changes therefore
cover the actual workflow operations with explicit access checks.

## 4. Verification Results

- API: **607 tests passed**, covering case services, ABAC service registration,
  effective ABAC rights, and dictionary/SQL case repository unit tests (SQLite).
- PPR: **314 tests passed**, with 14 existing third-party deprecation warnings.
- Regression tests cover allowed/denied parent access, bounded versus inverted
  queries, missing policy metadata, real commands and real effective ABAC models,
  sharing source/target permissions, and rejecting mixed write batches before any
  persistence. New membership objects with unset IDs are covered.
- PPR tests verify national collection grants for every generated organization
  user, restricted uploader add grants, phase target selection, the sharing
  request payload, and CaseSet creation/member-addition request behavior.
- A local HTTP replay using the actual generated query route and controlled
  service dependencies returns **403 with the original handler**, **200 `[]`
  with the patched handler**, and **403 for an inverted query**. OpenAPI still
  contains the same route. This verifies transport/command construction and the
  operation guard, not deployed authentication or database contents.
- Scoped API Black/isort checks, PPR Ruff lint/format checks, and both repositories'
  `git diff --check` passed. No new test directories were added.

Changes sit above repository interfaces and use common CRUD reads/writes; no
backend-specific behavior was introduced. SQLite/dictionary unit tests passed;
live SQL Server behavior was not tested.

## 5. Remaining Issues

The complete Locust test was not run, and no deployed API/IDP was restarted or
modified. The patched workflow is supported by focused and suite-level local
checks, but a successful live load test is **not yet established**. Restart the
API with the patch, provision the updated PPR policies, and run against a clean
test dataset to verify deployed authentication, cached policies, and persistence.

The supplied log also contains two separate problems outside this authorization
patch:

- Seven `retrieve/case_set_stats` requests contain the string `"None"` as the
  CaseSet ID and receive 422. `ColdMHSUser` converts the coordinator's optional
  ID to a string, even when no CaseSet was created.
- At 10:11:28, a COLD SeqDB upload reports ten failed samples because they already
  exist and `on_exists=ERROR`. HTTP 200 for that upload does not mean its per-item
  results succeeded.

These remain relevant to a full load-test rerun and are not evidence of the
membership permission failure being fixed or persisting.
