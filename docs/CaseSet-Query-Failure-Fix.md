# CaseSet query failure: cause and fix

## Observed problem

During the PPR run on 15 October 2026, ordinary organization users received HTTP
500 from `POST /v1/case_sets/query`. The command was `CaseSetCrudCommand` with
operation `READ_ALL` and a `DATETIME_RANGE` filter on `case_set_date`.

The original exception was:

```text
KeyError: UUID('01a13ffb-e3aa-9fa5-d377-ccf3870a71a3')
```

The UUID identifies a CaseSet, not a CaseType. Read-only inspection of the local
CaseDB SQLite data found that CaseSet, its existing CaseType, and its national
surveillance collection link. No missing CaseType was needed to cause the error.

## Why the query happened

PPR calls `LoginWorkflow.run()` from every scenario task, each iteration. It
simulates frontend data loading and is separate from creating or authenticating
users. HOT and COLD scenarios have independent coordination gates and run
concurrently.

In `gen-epix-ppr/output/iteration_details.csv`, run
`7da72ade-98b5-4fcd-9315-0e17238d9d57`, iteration 0:

| CSV line(s) | Europe/Amsterdam time | Event |
| --- | --- | --- |
| 69 | 16:33:46.364 | Last recorded HOT sample-upload response |
| 70–79 | From 16:33:46.371 | Ten HOT workers begin frontend login requests |
| 81 | 16:33:46.925 | Last recorded COLD sample-upload response |
| 137 | 16:33:51.529–16:33:55.813 | COLD CaseSet creation succeeds |
| 147–148, 150–157 | 16:33:55.811–16:33:57.007 | Ten HOT CaseSet queries fail |

The phase, concurrency, and gates identify the failing request group as HOT MHS
workers. The CSV does not record individual account or workflow identities.

## API defects

### Empty selection became an unrestricted association lookup

PPR supplied the upper bound `2026-10-15`, which the API parses as midnight.
The persisted CaseSet had `case_set_date = 2026-10-15 16:33:54.857889`, so it did
not match. The filtered CaseSet ID list was empty.

Previously, `_retrieve_case_set_data_collections_map()` converted an empty list
to `None`. The shared association helper interpreted `None` as unrestricted and
retrieved links for existing CaseSets. Meanwhile, the CaseType projection was
restricted to the empty CaseSet selection and returned no rows.

`_retrieve_case_sets_with_content_right()` then indexed its empty
`case_set_case_type_ids` dictionary with a linked CaseSet ID and raised `KeyError`,
before the PDP could evaluate that CaseSet's permissions.

This failure was reproduced with unchanged service functions and read-only
projections of the persisted data. Concurrent writes are not required.

### CaseType projection had the wrong shape and assumed row order

`read_fields(["case_type_id"])` returns one-element tuples, not scalar UUIDs.
Zipping those rows with an independently retrieved list of CaseSet IDs both
stored the wrong value type and assumed the two reads used identical ordering.
This could incorrectly filter otherwise readable CaseSets.

### SQL exception handling obscured the original error

`SAUnitOfWork._handle_exception()` replaced unexpected exceptions with
`NotImplementedError`, retaining the traceback but changing the exception type.
The original mapping error therefore appeared as an implementation placeholder.

## Changes applied

- In `gen_epix/casedb/services/case/crud_case_set.py`, return an empty list when
  no CaseSet IDs are selected. Build the CaseSet-to-CaseType dictionary from a
  single `read_fields(["id", "case_type_id"])` projection.
- In `gen_epix/casedb/services/case/service.py`, preserve explicit empty CaseSet
  and collection selections. The shared association helper returns an empty
  mapping if either supplied endpoint restriction is empty; `None` retains its
  unrestricted meaning. An empty iterator is also handled correctly.
- In `gen_epix/fastapp/repositories/sa/unit_of_work.py`, re-raise unexpected
  exceptions with their original type, value, and traceback. Existing SQL
  constraint translations, rollback, and session cleanup remain in place.

The existing DURING-phase CaseSet ABAC checks still evaluate nonempty selections.
List queries skip denied CaseSets; explicit requests still raise an authorization
error for denied CaseSets. No role grants or authorization bypasses were added.

The selection and projection fixes sit above the repository implementations.
Both dictionary and SQL repositories return projection tuples, so the new mapping
uses their common contract without backend-specific behavior.

## Regression coverage

- Empty date-query results while unrelated CaseSet links exist.
- Explicitly empty CaseSet selections.
- Reversed projection order and UUID-based CaseType lookup with the real PDP.
- Filtering denied CaseSets from list results and rejecting explicit denied reads.
- Empty lists and iterators for either association endpoint; unrestricted and
  nonempty selections retain their existing meanings.
- Original unexpected exceptions from both transaction bodies and commits;
  rollback, session cleanup, and unique-constraint translation.

Tests are in the existing CaseSet CRUD test module and the new mirrored
`test_casedb_unit_services_case_service.py` and
`test_fastapp_unit_repositories_sa_unit_of_work.py` modules. All use existing test
directories, so no VS Code launch-directory registration is needed.

Validation on Python 3.14.3: **324 tests passed** across CaseDB case services,
base PDP helpers, SQL repository tests (using in-memory SQLite), and dictionary
repository tests. The three directly affected test modules also passed their
individual runs. Black formatting, isort checks, and `git diff --check` passed
for the patch. No live SQL Server or deployed PPR smoke test was run.

## Follow-up verification

Restart the API with the patched source, then repeat a date query that matches no
CaseSets while other CaseSets and links exist. Expect HTTP 200 with `[]`. Repeat
with a matching date range and confirm that only authorized CaseSets are returned.
Then repeat the PPR run to verify the concurrent request sequence end to end.

PPR's date-only bound still excludes CaseSets created later that day. Changing it
to a full timestamp or an exclusive next-day boundary is a separate caller
behavior decision; the API must handle an empty result correctly regardless.
No PPR date semantics, deployed processes, or operational records were changed
by this API patch.
