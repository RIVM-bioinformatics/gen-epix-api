# LSP-3706: Further centralise ABAC logic

## Ticket

- Jira: [LSP-3706](https://rivm.atlassian.net/browse/LSP-3706)
- Type: Task
- Status when investigated: Under Review
- Branch: `LSP-3706-further-centralise-abac-logic`
- Branch base: `origin/dev` at `391adcff`

The ticket asks to inventory all uses of the ABAC rights classes, introduce an
`AbacPolicyDecisionPoint` instantiated for a user and their effective rights,
make it available through `RetrieveAbacPolicyDecisionPointCommand`, and replace
direct ABAC-class use with policy decision point calls.

## Current design

`AbacService` resolves and caches two snapshots:

- `CaseAbac`, containing effective case access and share records and the
  methods that interpret them.
- `RefDataAccess`, containing the reference-data scope and methods that build
  repository filters from it.

`CaseAbacPolicy` currently runs DURING case commands, stores these snapshots on
the command policy, and consumers recover them through
`BaseCaseAbacPolicy`. This distributes enforcement across case-service modules
and makes an absent policy double as an internal-command bypass.

## 1. Introduce `AbacPolicyDecisionPoint`

Add `AbacPolicyDecisionPoint` in
`gen_epix/casedb/domain/model/abac/policy_decision_point.py` and export it
through the ABAC and casedb model packages. It should be a plain domain object,
not a service and not a persistable Pydantic model. One instance represents the
effective case and reference-data rights of one user at one point in time.

The ABAC service owns policy retrieval, intersection, caching, and policy
decision point construction. The policy decision point owns interpretation and
enforcement of the resolved snapshots. It must not access repositories, call
`app.handle()`, or mutate the snapshots passed to it.

Proposed complete class signature:

```python
from collections.abc import Callable
from uuid import UUID

from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.domain.model.abac.rights import (
    CaseAbac,
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.casedb.domain.model.case import (
    CaseRights,
    CaseSetRights,
    RefDataAccess,
)
from gen_epix.filter import UuidSetFilter


class AbacPolicyDecisionPoint:
    def __init__(
        self,
        user_id: UUID,
        case_abac: CaseAbac,
        ref_data_access: RefDataAccess,
    ) -> None: ...

    @property
    def user_id(self) -> UUID: ...

    @property
    def has_full_case_access(self) -> bool: ...

    @property
    def has_full_ref_data_access(self) -> bool: ...

    def get_case_type_access_abacs(
        self, case_type_id: UUID
    ) -> dict[UUID, CaseTypeAccessAbac]: ...

    def get_case_type_share_abacs(
        self, case_type_id: UUID
    ) -> dict[UUID, CaseTypeShareAbac]: ...

    def get_case_rights(
        self,
        case_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights: ...

    def get_case_set_rights(
        self,
        case_set_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseSetRights: ...

    def get_combinations_with_any_rights(self) -> dict[UUID, set[UUID]]: ...

    def get_combinations_with_access_right(
        self, right: CaseRight
    ) -> dict[UUID, set[UUID]]: ...

    def get_case_types_with_any_rights(self) -> set[UUID]: ...

    def get_case_types_with_access_right(self, right: CaseRight) -> set[UUID]: ...

    def get_cols_with_any_rights(
        self, case_type_id: UUID | None = None
    ) -> set[UUID]: ...

    def get_cols_with_access_rights(
        self,
        right: CaseRight,
        case_type_id: UUID | None = None,
    ) -> set[UUID]: ...

    def get_data_collections_with_any_rights(self) -> set[UUID]: ...

    def get_data_collections_with_access_right_for_col(
        self,
        col_id: UUID,
        right: CaseRight,
    ) -> set[UUID]: ...

    def is_allowed(
        self,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        right: CaseRight,
        is_create_or_delete: bool = False,
        current_data_collection_ids: set[UUID] | None = None,
        tgt_data_collection_ids: set[UUID] | None = None,
    ) -> bool: ...

    def get_case_type_set_filter(
        self, field_name: str
    ) -> UuidSetFilter | None: ...

    def get_case_type_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def get_col_set_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def get_col_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def get_dim_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def get_ref_dim_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def get_ref_col_filter(self, field_name: str) -> UuidSetFilter | None: ...

    def _get_removable_data_collection_ids(
        self,
        is_case_set: bool,
        data_collection_ids: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
        is_own_private: bool,
    ) -> set[UUID]: ...

    def _get_addable_data_collection_ids(
        self,
        is_case_set: bool,
        data_collection_ids: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
        is_own_private: bool,
    ) -> set[UUID]: ...

    def _is_content_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        is_create_or_delete: bool,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool: ...

    def _update_access_rights(
        self,
        right: CaseRight,
        result: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
    ) -> set[UUID]: ...

    def _validate_private_creation_or_deletion(
        self,
        right: CaseRight,
        created_in_data_collection_id: UUID,
        access_abac: dict[UUID, CaseTypeAccessAbac],
    ) -> bool: ...

    def _check_access_or_share(
        self,
        right: CaseRight,
        data_collection_id: UUID,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        current_data_collection_ids: set[UUID],
    ) -> bool: ...

    def _is_add_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        is_create_or_delete: bool,
        created_in_data_collection_id: UUID,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool: ...

    def _is_remove_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        is_create_or_delete: bool,
        created_in_data_collection_id: UUID,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool: ...

    def _get_case_or_set_rights_with_full_access(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights: ...

    def _get_case_or_set_rights_without_full_access(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights: ...

    def _update_data_collections_with_share_rights(
        self,
        share: dict[UUID, CaseTypeShareAbac],
        is_case_set: bool,
        data_collection_ids: set[UUID],
        add_data_collection_ids: set[UUID],
        remove_data_collection_ids: set[UUID],
    ) -> None: ...

    def _get_case_or_set_rights(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights: ...

    @staticmethod
    def _get_has_right_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeAccessAbac | CaseTypeShareAbac], bool]: ...

    @staticmethod
    def _get_share_source_ids_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeShareAbac], set[UUID]]: ...

    def _get_ref_data_filter(
        self,
        field_name: str,
        members: set[UUID],
    ) -> UuidSetFilter | None: ...
```

There are no proposed public class methods. The two static helpers are pure
right-to-accessor mappings. Duplicate existing share-accessor helpers should be
consolidated into `_get_share_source_ids_function` during the move.

The constructor validates that `ref_data_access.user_id` matches `user_id`.
`CaseAbac` currently carries no user ID, so its association with the user is
guaranteed by constructing both snapshots in the same ABAC service handler.
Construction without a persisted user is rejected; internal no-ABAC operations
continue through their explicit service path and do not receive a policy
decision point.

The two `get_case_type_*_abacs()` methods return shallow copies so callers can
inspect records needed for filtering and response projection without receiving
the policy decision point's mutable dictionaries. Longer term, those accessors can be
replaced by narrower queries, but that is not required for this behavior-
preserving refactor.

## 2. Move ABAC interpretation behind the policy decision point

Move all behavioral methods from `CaseAbac` to `AbacPolicyDecisionPoint`,
keeping `CaseAbac`, `CaseTypeAccessAbac`, and `CaseTypeShareAbac` as
resolved-rights data structures. Move the filter-building methods from
`RefDataAccess` to the policy decision point and leave `RefDataAccess` as a
reference-scope data structure.

The first implementation should preserve the existing method names and
signatures where practical. This makes each consumer replacement mechanical
and allows the existing rights tests to be retargeted to the policy decision
point without changing expected behavior. Private helpers move with their
public methods; they are listed in the complete signature above to make the
ownership boundary explicit.

Replace the following categories of direct use:

| Consumer category | Current access | Policy decision point replacement |
| --- | --- | --- |
| Case and case-set create/delete | `CaseAbac.is_allowed()` | `policy_decision_point.is_allowed()` |
| Case and case-set rights response | `get_case_rights()` / `get_case_set_rights()` | Same methods on policy decision point |
| Query and repository filtering | Accessible case types, collections, and columns | Same query methods on policy decision point |
| Complete case-type projection | Nested access/share maps | `get_case_type_access_abacs()` and `get_case_type_share_abacs()` |
| Sequence/file authorization | Full-access flag and per-column collections | Policy decision point property and query method |
| Statistics, similarity, own-case checks | Full-access flag and readable combinations | Policy decision point property and query methods |
| Reference-data CRUD | `RefDataAccess.get_*_filter()` | `policy_decision_point.get_*_filter()` |

The production inventory covers these modules:

- `gen_epix/casedb/services/case/create_case_set.py`
- `gen_epix/casedb/services/case/create_seq.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/crud_case_set.py`
- Case, case-set, identifier, member, and data-collection-link CRUD modules
- Case-type, case-type-set, column, dimension, ref-column, and ref-dimension
  CRUD modules
- `retrieve_case.py`, `retrieve_complete_case_type.py`,
  `retrieve_is_own_cases.py`, `retrieve_seq.py`,
  `retrieve_similar_cases.py`, and `retrieve_stats.py`
- `gen_epix/casedb/services/case/service.py` and upload helpers that receive
  rights snapshots or complete case-type projections

Do not expose `CaseAbac` or `RefDataAccess` from the policy decision point as
public properties. That would retain the coupling this ticket is intended to
remove.

## 3. Add policy decision point retrieval command

1. Define `RetrieveAbacPolicyDecisionPointCommand(Command)` in
   `gen_epix/casedb/domain/command/abac.py`. It needs no request fields beyond
   the inherited authenticated `user`.
2. Export it from `gen_epix/casedb/domain/command/__init__.py` and add it to
   `COMMANDS_BY_SERVICE_TYPE[ServiceType.ABAC]`.
3. Extend `BaseAbacService.register_handlers()` to register
    `retrieve_abac_policy_decision_point` and add the corresponding abstract
    method.
4. Implement the handler in `gen_epix/casedb/services/abac.py`. Require a user
   with a persisted ID, obtain both snapshots through the existing cached
    resolution paths, and return a new policy decision point.
5. Do not expose an API route for this internal application command.

## 4. Replace policy-content retrieval

Case-service entry points should retrieve the policy decision point through:

```python
policy_decision_point = self.app.handle(
    command.RetrieveAbacPolicyDecisionPointCommand(user=cmd.user)
)
```

Pass the policy decision point through internal helper calls that already pass
`CaseAbac` so one top-level command causes one policy decision point retrieval.
Do not repeatedly dispatch the retrieval command inside loops.

For CRUD paths, replace `get_case_abac_from_command()` and
`get_ref_data_access_from_command()` with one helper that retrieves a policy
decision point for ABAC-controlled commands. `NO_ABAC_COMMAND_CLASSES` retain
an explicit `None` policy decision point/internal bypass. Do not infer bypass
from a missing policy.

## 5. Retire case ABAC DURING policy use

After every consumer uses the policy decision point command:

1. Remove `CASE_ABAC_COMMANDS` from the casedb ABAC service contract.
2. Stop registering `CaseAbacPolicy` at `EventTiming.DURING`.
3. Remove `BaseCaseAbacPolicy` and `CaseAbacPolicy` if no reference-data or
   compatibility use remains.
4. Remove command-policy extraction helpers from `crud_common.py`.

RBAC remains unchanged. The new retrieval command goes through normal
`App.handle()` dispatch and permission checks. ABAC policy CRUD authorization
also remains unchanged. This removes DURING only as the transport for resolved
case/reference ABAC snapshots; it does not remove authorization checks.

## 6. Preserve cache and backend behavior

- Keep effective-rights calculation and TTL caches in `AbacService`.
- Keep invalidation for user/organization access policies, share policies, and
  organization changes.
- Construct policy decision points from cached snapshots; do not cache policy
    decision point instances separately unless profiling demonstrates a need.
- No repository query semantics should change. DICT, SA_SQLITE, and SA_SQL
  parity is therefore expected to be unaffected and must be confirmed by the
  existing integration tests.

## 7. Tests

1. Retarget `test/casedb/unit/domain/model/abac/test_rights.py` to instantiate
    `AbacPolicyDecisionPoint` and preserve all existing rights-calculation cases.
2. Add policy decision point tests for constructor identity validation, full
    case access, full reference access, defensive map accessors, invalid rights,
    and empty scopes.
3. Extend `test/casedb/unit/services/abac/test_casedb_abac.py` for handler
   registration, authenticated retrieval, missing user/ID rejection, snapshot
   reuse, and cache invalidation.
4. Update focused case-service tests to mock or provide a policy decision point
    instead of policy content. Preserve tests for create/delete, sharing,
    content reads and writes, sequence access, statistics, and reference-data
    filters.
5. Add a command-lifecycle test proving policy decision point retrieval works
    without the old DURING policy and does not recurse through case ABAC
    handling.
6. Run casedb operational-data and reference-data integration tests to verify
   unchanged authorization behavior across repository implementations.

## 8. Validation order

1. Policy decision point unit tests.
2. ABAC service unit tests.
3. Each touched case-service unit-test scope after its migration.
4. Casedb data-access integration tests.
5. Isort and Black checks for touched files.
6. Mypy and pylint for the changed package, recording any pre-existing output.
7. `python run.py test_all` as final regression validation.

## Expected behavior impact

- Roles and RBAC permissions: unchanged.
- ABAC rules and effective-rights intersection: unchanged.
- Policy timing: case/reference rights are no longer transported through a
    DURING policy; enforcement is invoked explicitly through the policy decision
    point.
- Root and `NONE` IDP behavior: unchanged because user resolution and root
  fallback are outside this refactor.
- API and OpenAPI surface: unchanged; the retrieval command is internal.
- Repository behavior and schemas: unchanged.