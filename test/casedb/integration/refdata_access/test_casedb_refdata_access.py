import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.refdata_access.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from uuid import UUID

import pytest
from cachetools import LRUCache, cached

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.enum import RoleSet
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


# TODO: scenario IDs to be updated (currently copied from test_casedb_content)
@pytest.mark.scenario_ids(
    "TC-RBAC-04-07",
    "TC-RBAC-04-20",
    "TC-RBAC-04-10",
    "TC-RBAC-04-12",
    "TC-RBAC-04-06",
    "TC-RBAC-04-06",
    "TC-RBAC-04-08",
    "TC-RBAC-04-09",
)
class TestRefdataAccess:

    @cached(cache=LRUCache(maxsize=1))
    def _get_root_user(self, env: Env) -> model.User:
        return env.get_root_user()

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_users(self, env: Env) -> list[model.User]:
        retval: list[model.User] = self._read_all(env, model.User, sort=True, return_id=False)  # type: ignore[assignment]
        return retval

    @cached(
        cache=LRUCache(maxsize=1024),
        key=lambda self, env, user, role_set: (user.id, role_set),
    )
    def _has_role(self, env: Env, user: model.User, role_set: enum.RoleSet) -> bool:
        retval = bool(user.roles & {x for x in env.app.impl.role_set_map[role_set]})
        return retval

    def _read_all(
        self,
        env: Env,
        model_class: type[model.Model],
        user: model.User | None = None,
        sort: bool = True,
        return_id: bool = True,
    ) -> list[model.Model] | list[UUID]:
        if user is None:
            user = self._get_root_user(env)
        command_class = env.app.domain.get_crud_command_for_model(model_class)
        retval: list[model.Model] | list[UUID] = env.app.handle(
            command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
                props={"return_id": return_id},
            )
        )
        if sort:
            if return_id:
                retval.sort(key=lambda x: x)
            else:
                retval.sort(key=lambda x: x.id)
        return retval

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_disease(self, env: Env) -> None:
        all_diseases = self._read_all(env, model.Disease)
        for user in self._get_all_users(env):
            diseases = self._read_all(env, model.Disease, user=user)
            assert diseases == all_diseases

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_etiology(self, env: Env) -> None:
        all_etiologies = self._read_all(env, model.Etiology)
        for user in self._get_all_users(env):
            etiologies = self._read_all(env, model.Etiology, user=user)
            assert etiologies == all_etiologies

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_concept(self, env: Env) -> None:
        all_concepts = self._read_all(env, model.Concept)
        for user in self._get_all_users(env):
            concepts = self._read_all(env, model.Concept, user=user)
            assert concepts == all_concepts

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_concept_set(self, env: Env) -> None:
        all_concept_sets = self._read_all(env, model.ConceptSet)
        for user in self._get_all_users(env):
            concept_sets = self._read_all(env, model.ConceptSet, user=user)
            assert concept_sets == all_concept_sets

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_region(self, env: Env) -> None:
        all_regions = self._read_all(env, model.Region)
        for user in self._get_all_users(env):
            regions = self._read_all(env, model.Region, user=user)
            assert regions == all_regions

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_region_set(self, env: Env) -> None:
        all_region_sets = self._read_all(env, model.RegionSet)
        for user in self._get_all_users(env):
            region_sets = self._read_all(env, model.RegionSet, user=user)
            assert region_sets == all_region_sets

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_dim(self, env: Env) -> None:
        all_dims = self._read_all(env, model.Dim)
        for user in self._get_all_users(env):
            dims = self._read_all(env, model.Dim, user=user)
            assert dims == all_dims

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_col(self, env: Env) -> None:
        all_cols = self._read_all(env, model.Col)
        for user in self._get_all_users(env):
            cols = self._read_all(env, model.Col, user=user)
            assert cols == all_cols

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_case_type_set_category(self, env: Env) -> None:
        all_case_type_set_categories = self._read_all(env, model.CaseTypeSetCategory)
        for user in self._get_all_users(env):
            case_type_set_categories = self._read_all(
                env, model.CaseTypeSetCategory, user=user
            )
            assert case_type_set_categories == all_case_type_set_categories

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_case_set_category(self, env: Env) -> None:
        all_case_set_categories = self._read_all(env, model.CaseSetCategory)
        for user in self._get_all_users(env):
            case_set_categories = self._read_all(env, model.CaseSetCategory, user=user)
            assert case_set_categories == all_case_set_categories

    def test_case_type(self, env: Env) -> None:
        all_case_types = self._read_all(env, model.CaseType)
        for user in self._get_all_users(env):
            if self._has_role(env, user, RoleSet.GE_REFDATA_ADMIN):
                case_types = self._read_all(env, model.CaseType, user=user)
            else:
                pass
                # TODO: filter case_types by ABAC
                print(
                    f"Skipping ABAC filtering for non-admin users in test_case_type: {user.roles}"
                )
                continue
            assert case_types == all_case_types

    # TODO: Add tests for all other refdata models
