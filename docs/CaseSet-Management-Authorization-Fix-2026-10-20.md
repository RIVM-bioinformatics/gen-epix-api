# CaseSet management authorization failure: investigation and fix

Investigated on 20 October 2026 against API HEAD `506e1feb`, PPR HEAD
`e51cb08`, and lsp-data HEAD `c21f547b`, including their existing working-tree
changes. The older `IMPLEMENTATION_PLAN.md` and investigation documents were
read as historical evidence and left intact. This report describes this run and
the current implementation; historical test results are not counted as new tests.

## 1. Root Cause

The current API rejects operations required by the workflow before checking its
collection permissions. There are two separate failures in the supplied run:

1. `POST /v1/case_data_collection_links/batch` constructs
   `CaseDataCollectionLinkCrudCommand(CREATE_SOME)`. For a non-exempt user,
   `_crud_case_data_collection_link_with_abac()` rejected every write with
   diagnostic `7fe2e531`. The existing PPR patch enabled this previously
   commented-out sharing request, exposing that restriction.
2. `POST /v1/case_set_members/query` constructs
   `CaseSetMemberCrudCommand(READ_ALL)`, even when the body explicitly selects
   case UUIDs. `_crud_case_set_member_with_abac()` rejected every `READ_ALL`
   with diagnostic `85539cf8`. A filter does not change the CRUD operation to
   `READ_SOME`, which expects membership-record IDs.

The same API restrictions would also block later member insertion and querying
a CaseSet's collection links. Removing the first failing request would leave
those operations broken and would change the test's intended behavior.

Commit `0ea71503` (18 October, PR #790) introduced these operation guards into
the checked-out history. Previously these services used temporary CRUD
delegation with incomplete authorization. Commit `881589c7` had centralized
exemption dispatch earlier; it did not introduce these guards. The locally
available CaseSetMember branch commit `1bfaf00f7` has the same three association
service implementations as current HEAD. Merging those implementations cannot
remove the observed restrictions.

A second API issue matters when allowing the filtered reads:
`CaseSetMemberCrudCommand` was present in `ABAC_EXEMPTED_ROLE_SET_MAP`, but
absent from `CASE_ABAC_COMMANDS`. Consequently the normal `App.handle()`
lifecycle did not attach its DURING-phase `CaseAbacPolicy`. The old
no-metadata fallback delegated directly to CRUD. Allowing queries without
registering that policy would leave parent access checks ineffective.

The existing PPR patch correctly addresses earlier sharing mistakes: it uses
the uploader's credentials, shares before publishing cases to consumers, and
uses the same phase collection for cases and CaseSets. It cannot repair an API
operation guard. No additional PPR permission expansion is needed for this fix.

## 2. Investigation Findings

### Log correlation: the examples are different requests

The supplied PPR log and `output/iteration_details.csv` agree on **158 requests**
for run `96fe5726-44e2-453f-b56c-98efda7a797b`: **155 HTTP 200s and three
HTTP 403s**. Twenty successful case-upload requests preceded the denials.
The application log reports 100 COLD and 1,000 HOT cases uploaded successfully.

| PPR log line | Local time (Europe/Amsterdam) | User | Request |
| --- | --- | --- | --- |
| 30 | 12:12:50 | `org-user0@ppr.lab53...` | COLD case-collection link batch; 403 |
| 31 | 12:12:50 | `org-user3@ppr.phi0...` | HOT case-collection link batch; 403 |
| 34 | 12:12:50 | `org-user0@ppr.phi0...` | COLD membership query; 403 |

The supplied API exception names the **third user and membership command**.
Its `10:12:50.441Z` timestamp is `12:12:50.441` locally. It is strongly
consistent with line 34, not line 30. There is no shared request ID proving an
exact one-to-one match. The email difference is explained by independent
requests from different actors, without evidence of a token/user mix-up.

The case-link request does **not** trigger a nested membership command: its
restricted handler rejected `CREATE_SOME` before such a call could happen.
The separate PHI task triggers the membership query.

No CaseSet creation or member-insertion request appears in this run. Payload
case UUIDs are not recorded, so exact selected cases cannot be recovered.
Historical reports refer to a different run with many membership errors;
their counts, statistics errors and sample-duplicate errors are not observations
from this supplied run.

### gen-epix-ppr: complete relevant flow

`Manager` loads `RefDataLoader` before Locust users start. The log confirms
201 organizations, 1,206 users, 201 private collections, 201 organization-admin
policies, 804 organization access policies and 4,020 user access policies
provisioned by 12:10:56. Uploads begin at 12:12:04.

| Phase | Uploading actor and origin | Sharing target | CaseSet actor and origin |
| --- | --- | --- | --- |
| HOT/COVID | PHI ordinary user; PHI-private collection | `cfg.get_data_collection_id(Phase.HOT)` | MHS ordinary users; each MHS-private collection |
| COLD/Salmonella | LAB ordinary user; LAB-private collection | `cfg.get_data_collection_id(Phase.COLD)` | PHI ordinary user; PHI-private collection |

The role for these actors is `CASEDB_ORG_USER`. Organization administrators
are separately generated; the workflow does not switch to them for these calls.

The HOT uploader shares before storing uploaded case IDs and opening the upload
gate. MHS workers then claim separate chunks and create regional CaseSets. The
COLD uploader shares before storing case/sample batches. The PHI waits for that
gate, uploads the sample batches, then uses the first ten case IDs. It creates
one national CaseSet and adds cases to that same set in subsequent iterations.

`create_case_set()` performs these requests in order:

1. Read categories, statuses and collections.
2. Query existing memberships by case IDs.
3. Create the CaseSet with a private origin, initial members and a national link.
4. Retrieve case rights and query case IDs.
5. Query memberships again and return the new set ID.

`add_cases_to_existing_event()` queries current members, CaseSet collection links
and memberships of the new cases; inserts new members; queries updated members,
case rights and case IDs; queries the combined memberships; retrieves statistics.
The read workflow in `view_case_set_or_case_type.py` also queries memberships by
case IDs, so it benefits from the same corrected, permission-filtered API path.

The retained sharing patch is logically necessary: consumer users have national
case read access, but no national case-column write access and no write access
to another organization's private source. Late sharing by those consumers would
not satisfy source write authorization. Their CaseSet read/write rights are
separate from case-column write rights.

The COLD uploader releases its gate in `finally`, even if sharing fails before
publishing state. The observed PHI log says zero sample units. Code therefore
explains how the PHI can continue after the LAB error, probably with empty case
IDs in iteration zero. The payload is absent, so that last detail remains an
inference. Failure propagation through the coordinator is a separate issue and
was not changed here.

### gen-epix-api: authorization contract

The generated routes construct commands and dispatch through `App.handle()`.
RBAC permits the association CRUD commands for organization users. Service
ABAC determines which operations and resources they may actually access.
Only app-admin-or-higher roles are exempted for these associations.

`AbacService` intersects active organization and user policies by case type and
collection. Being in an organization, knowing a UUID or having a user-side flag
alone is insufficient. `CaseAbac.is_allowed()` implements content access through
current collections, and add permissions through target access or source-based
share policies. The fix uses that existing implementation.

Membership reads need both `READ_CASE` and `READ_CASE_SET`. Insertion needs
`READ_CASE`, `WRITE_CASE_SET`, and matching case types. Sharing requires
`WRITE_CASE` through an existing collection and `ADD_CASE` for the target.
All requested write items are checked before delegated persistence.

`CreateCaseSetCommand` already supports initial memberships and collection links.
Its PDP requires a private creation collection and permission to add the set to
the requested additional collections. Creating directly in a national collection
would conflict with that private-origin rule. There is no replacement sharing
or member-insertion command/endpoint implemented in this checkout that PPR can
switch to while preserving the workflow.

### lsp-data: source, generated data and loading

The pipeline reads `data/commondb/src/organization.xlsx` for organizations,
users and collections, and `data/casedb/src/abac.xlsx` for case policies.
`lsp_data/dataset/casedb/cfg.py` selects these source tables; the transformer
validates them through an offline composed app and emits per-dataset CSVs,
JSON archives and service-split pickles. Dataset membership uses `dm.datasets`.
Both phase collection source rows include `DEMO; PPR_TEST`.

`lsp_data/task/apply_refdata/loader.py` loads service-split `db.*.pkl.gz`
in service dependency order, falling back to a legacy single pickle. It syncs
models in dependency order, skips User models, and does not delete absent
remote rows during ordinary sync. Consequently generated CSVs alone cannot
prove which data or stale rows are present in a deployed environment.

The checked-in `PPR_TEST` pickles, JSON archives and CSVs were inspected:

- There is one static organization and two static user rows. PPR-generated
  organizations/users and their policies are supplied by PPR, not by these rows.
- Organization/user case-access and share-policy tables are empty in this
  dataset. This is consistent with PPR provisioning its own active policies.
- Both configured national targets and all three referenced column sets exist.
  The all-notifiable-case-types set includes Salmonellosis and COVID-19.
- The all-column set has 49 Salmonellosis and 53 COVID-19 columns. The national
  surveillance read set has 18 and 14 respectively; the event read set has
  49 and 53. There is no empty read-set explanation for the operation guard.

| PPR field | UUID | Current lsp-data collection name |
| --- | --- | --- |
| `national_surveillance_data_collection_id` / COLD | `018d074d-e9fc-5c35-9d3c-4bbdbaf851d2` | National - Surveillance clinical laboratories |
| `national_event_data_collection_id` / HOT | `01918870-0a02-15c2-f48b-5432ab38c754` | National - Surveillance municipal health services and clinical laboratories |

The HOT field name does not match the current metadata label, but upload sharing
and CaseSet creation use the same UUID. Changing it based only on that label
would change the scenario and cannot fix the guard, so it was retained.

One unrelated mismatch is confirmed: PPR's generic `shared_data_collection_id`
(`0191079f-0377-3790-a874-b6161db8bc6d`) is absent from checked-in PPR_TEST,
DEMO and API demo organization data, although PPR still generates a policy for
it. The corrected phase-sharing calls do not use it. Successful provisioning
does not prove that every cross-service foreign key exists. This may matter to
other callers or a fresh environment, but is not the cause of the observed
operation-level 403s. No workbook or dataset regeneration is justified for this
specific fix. Actual deployed rows and policy caches remain unverified.

## 3. Implemented Solution

The new implementation changes only API service authorization and policy
registration, with tests and this report:

1. Register `CaseSetMemberCrudCommand` for the existing DURING-phase case ABAC
   policy. Non-exempt membership commands without metadata now fail closed.
2. Allow membership queries only with non-inverted UUID-set selections on
   `case_id` or `case_set_id`. Apply the existing checks on both parents.
3. Allow member creation only after every case is readable, every CaseSet is
   writable and types match. Keep members whose IDs are still unset until CRUD
   assigns them; reject an entire unauthorized batch before writing.
4. Allow CaseSet collection-link queries with non-inverted `case_set_id`
   UUID-set selections, retaining the existing per-linked-collection read check.
5. Allow case sharing only after checking source write and target add rights
   for every link. Updates, deletes and unrestricted enumeration stay rejected
   on these restricted association paths.

This preserves command-centric authorization, existing routes, schemas, RBAC
roles and repository interfaces. No new role grants or permission records are
introduced by this session. Diagnostic IDs were generated using the repository's
collision-checked hex-code skill.

A PPR-only change cannot correct the unconditional guards. Removing requests
would reduce coverage and leave later writes unsupported. Switching to an admin,
changing private origins, or restoring the old unrestricted delegation would
change the trust model. Adding new endpoints would duplicate the existing
association contracts. The focused API changes are the smallest complete option
for the retained workflow. The historical plan's four service/policy changes
were independently confirmed as necessary; its focused tests were reused and
supplemented with actual composed-app HTTP coverage.

## 4. Changes by Repository and File

### gen-epix-api: files changed in this investigation

| File | Function/class/section | Change and reason |
| --- | --- | --- |
| `gen_epix/casedb/domain/service/abac.py` | `BaseAbacService.CASE_ABAC_COMMANDS` | Register membership commands so dispatched calls receive real case ABAC metadata. |
| `gen_epix/casedb/services/case/crud_case_set_member.py` | `_crud_case_set_member_with_abac` | Support explicit filtered reads and authorized creation; reject missing metadata; keep parent checks and validate full batches before writing. |
| `gen_epix/casedb/services/case/crud_case_data_collection_link.py` | `_crud_case_data_collection_link_with_abac` | Authorize sharing with source write and target add checks before persistence. |
| `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py` | `_crud_case_set_data_collection_link_with_abac` | Permit explicit CaseSet queries while preserving linked-collection checks. |
| `test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_set_member.py` | `TestCaseSetMemberCrud` | Cover filtered reads, registration, private/shared parent access, missing metadata, creation rights and mixed-batch rejection. |
| `test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_data_collection_link.py` | `TestCaseDataCollectionLinkCrud` | Cover real ABAC source/target decisions and rejection before any mixed-batch write. |
| `test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_set_data_collection_link.py` | `TestCaseSetDataCollectionLinkCrud` | Cover allowed and denied filtered CaseSet-link queries. |
| `test/casedb/integration/data_access/test_case_set_management_authorization.py` | `authorization_env`, `test_http_sharing_and_membership_lifecycle` | New HTTP regression using composed apps, real policy resolution and dictionary/SQLite repositories; cover both the workflow and denied cases. |
| `docs/CaseSet-Management-Authorization-Fix-2026-10-20.md` | Entire document | Record current root cause, log correlation, alternatives, exact scope and validation. |

### gen-epix-ppr: existing changes reviewed and retained

No file was changed in this repository during this investigation. These earlier
uncommitted changes are relevant to the combined working solution:

| File | Relevant section | Existing change retained and why |
| --- | --- | --- |
| `gen_epix_ppr/share_uploaded_cases_in_data_collection.py` | `run` | Enable sharing using the supplied uploader and target. |
| `gen_epix_ppr/locustfile.py` | HOT PHI and COLD LAB tasks | Select phase targets before publishing cases to consumers. |
| `gen_epix_ppr/ref_data_manager.py` | Organization access-policy builder | Permit PHI adding cases to HOT and LAB adding cases to COLD; preserve MHS and national column-write/remove restrictions. |
| `gen_epix_ppr/case_set_management.py` | Creation and member-addition methods | Remove late consumer sharing; preserve private CaseSet origins and all membership operations. |
| `tests/test_case_set_management.py` | Workflow/sharing tests | Assert request payloads, private-origin/national-target separation and no late sharing. |
| `tests/test_phase_propagation.py` | Phase tests | Assert HOT/COLD sharing targets and request context. |
| `tests/test_ref_data_manager.py` | Policy tests | Assert uploader-only national add grants and generated users' national read/CaseSet rights. |

### lsp-data and unrelated working-tree changes

No lsp-data files were changed. Existing API configuration, limiter, launch,
lockfile and historical documentation changes, PPR authentication/generator and
other pre-existing changes, and lsp-data's existing lockfile change were left
untouched. Generated test reports/caches are not hand-authored patch files.
No commit, push, migration or service restart was performed.

## 5. Validation Results

### Executed checks

| Check | Result |
| --- | --- |
| Focused regression tests before source changes | 15 failed, 48 passed: failures reproduced the guards, absent registration and permissive metadata fallback. |
| Same focused tests after source changes | 63 passed. |
| Broader API case services, ABAC services/domain/rights and dictionary/SA repository unit tests | 607 passed. |
| New composed-app HTTP regression | Passed on both DICT_EMPTY and SA_SQLITE_EMPTY. |
| Final combined API selection (unit tests plus new HTTP integration test) | 609 passed; two SlowAPI deprecation warnings. |
| Full PPR pytest suite | 314 passed; 14 third-party deprecation warnings. |
| Scoped API Black/isort and PPR Ruff lint/format | Passed. |
| API and PPR `git diff --check` | Passed. |
| Reference-data inspection | Source dataset tags, CSV/JSON/pickle targets, case-type membership and nonempty column sets checked without editing/rebuilding. |

The new HTTP regression seeds private-origin cases and persists actual policies.
It injects persisted ordinary-user identities in place of external token
validation. Routes, `App.handle()`, RBAC, DURING policy registration, effective
organization/user rights, association checks and persistence are real. It covers
sharing, initial CaseSet creation, subsequent member insertion, inaccessible
parents/outsiders, a user without CaseSet write access in an otherwise permitted
organization, mismatched case types, inverted/unrestricted reads and rejection
of mixed write batches with no partial rows left behind.

A separate scratch HTTP comparison loads the original handlers from Git HEAD,
omits membership policy registration as HEAD did, then compares the
working implementation on fresh dictionary and SQLite composed apps:

| Request | Original | Patched, authorized user |
| --- | --- | --- |
| Case sharing batch | 403 | 201 |
| Membership query by case UUID | 403 | 200 |
| Member insertion batch | 403 | 201 |
| CaseSet collection-link query | 403 | 200 |
| Inverted membership query | 403 | 403 |

This reproduces and resolves the operation-level failures locally with real
authorization. It does not establish a successful deployed Locust run.
Scratch evidence is under `/tmp/caseset-before-tests.log`,
`/tmp/caseset-after-tests.log`, `/tmp/caseset-api-suite.log`,
`/tmp/caseset-integration.log`, `/tmp/caseset-ppr-suite.log`, and
`/tmp/caseset-http-comparison.log`. The comparison script is
`/tmp/caseset_compare_handlers.py`; the final combined API log is
`/tmp/caseset-api-final.log`. These are temporary verification artifacts.

Re-run the persistent checks from each repository root, using its own existing
virtual environment (API Python 3.14.3; PPR Python 3.9.19 in this session):

```bash
# gen-epix-api: the final combined 609-test selection
.venv/bin/python -m pytest -q \
  test/casedb/unit/services/case \
  test/casedb/unit/services/test_casedb_unit_services_abac.py \
  test/casedb/unit/domain/service/test_casedb_unit_domain_service_abac.py \
  test/casedb/unit/domain/model/abac/test_casedb_unit_domain_model_abac_rights.py \
  test/casedb/unit/repositories/test_casedb_unit_repositories_case_dict.py \
  test/casedb/unit/repositories/test_casedb_unit_repositories_case_sa.py \
  test/casedb/integration/data_access/test_case_set_management_authorization.py

# gen-epix-ppr: the full suite
PYTHONPATH=. .venv/bin/python -m pytest
```

### Limits and remaining verification

Both configured local API OpenAPI probes on `127.0.0.1:8000` and `:8001`
failed to connect from this execution environment. The default Locust config
also specifies 33 users and a two-hour run. A complete live Locust run was not
performed. No existing service, Keycloak realm, live dataset or policy cache was
modified to manufacture a passing run.

External JWT/Keycloak validation, deployed data/cache consistency, SQL Server,
concurrent load and downstream SeqDB processing remain unverified. Run the
updated API with the retained PPR patch and provisioned policies against the
intended test environment to validate those boundaries. The generic collection
default, misleading HOT collection name and coordinator failure propagation
remain separate observations; this patch does not claim to resolve them.
