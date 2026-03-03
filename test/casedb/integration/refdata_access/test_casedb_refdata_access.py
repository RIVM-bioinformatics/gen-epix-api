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
from rich import print

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.enum import RoleSet
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
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

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_organization_access_case_policies(
        self, env: Env
    ) -> list[model.OrganizationAccessCasePolicy]:
        retval: list[model.OrganizationAccessCasePolicy] = self._read_all(
            env, model.OrganizationAccessCasePolicy, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_organization_share_case_policies(
        self, env: Env
    ) -> list[model.OrganizationShareCasePolicy]:
        retval: list[model.OrganizationShareCasePolicy] = self._read_all(
            env, model.OrganizationShareCasePolicy, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_user_access_case_policies(
        self, env: Env
    ) -> list[model.UserAccessCasePolicy]:
        retval: list[model.UserAccessCasePolicy] = self._read_all(
            env, model.UserAccessCasePolicy, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_user_share_case_policies(
        self, env: Env
    ) -> list[model.UserShareCasePolicy]:
        retval: list[model.UserShareCasePolicy] = self._read_all(
            env, model.UserShareCasePolicy, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_case_type_set_members(self, env: Env) -> list[model.CaseTypeSetMember]:
        retval: list[model.CaseTypeSetMember] = self._read_all(
            env, model.CaseTypeSetMember, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_case_type_sets(self, env: Env) -> list[model.CaseTypeSet]:
        retval: list[model.CaseTypeSet] = self._read_all(
            env, model.CaseTypeSet, return_id=False
        )  # type: ignore[assignment]
        return retval

    @cached(cache=LRUCache(maxsize=1))
    def _get_all_organizations(self, env: Env) -> list[model.Organization]:
        retval: list[model.Organization] = self._read_all(
            env, model.Organization, return_id=False
        )  # type: ignore[assignment]
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

    def _get_expected_case_type_ids_for_reference_data(
        self,
        env: Env,
        user: model.User,
    ) -> set[UUID]:
        """
        Get expected case type IDs for reference data access.

        For reference data, the actual rights of organization users are limited to read rights
        and are the union of the reference data available to the organization through the
        organization (access/share) policies. This means all users of the same organization
        see the same reference data.

        Logic:
        - Organization access policies OR organization share policies (union) = org_case_type_ids
        - All users in the same organization have the same reference data access
        """
        # Get all the reference data using cached methods
        all_organization_access_case_policies = (
            self._get_all_organization_access_case_policies(env)
        )
        all_organization_share_case_policies = (
            self._get_all_organization_share_case_policies(env)
        )
        all_case_type_set_members = self._get_all_case_type_set_members(env)

        # Get case type sets from organization access policies for this user's org
        org_access_case_type_set_ids = {
            x.case_type_set_id
            for x in all_organization_access_case_policies
            if x.organization_id == user.organization_id
        }

        # Get case type sets from organization share policies for this user's org
        org_share_case_type_set_ids = {
            x.case_type_set_id
            for x in all_organization_share_case_policies
            if x.organization_id == user.organization_id
        }

        # Get all case types accessible through organization access policies
        org_access_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in org_access_case_type_set_ids
        }

        # Get all case types accessible through organization share policies
        org_share_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in org_share_case_type_set_ids
        }

        # Union: case types accessible through organization access OR share policies
        expected_case_type_ids = org_access_case_type_ids | org_share_case_type_ids

        if VERBOSE:
            all_case_type_sets = self._get_all_case_type_sets(env)
            case_type_set_name_map = {cts.id: cts.name for cts in all_case_type_sets}

            org_access_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in org_access_case_type_set_ids
            ]
            org_share_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in org_share_case_type_set_ids
            ]

            print(
                "org access case type sets:",
                len(org_access_case_type_set_ids),
                org_access_case_type_set_names,
            )
            print(
                "org share case type sets:",
                len(org_share_case_type_set_ids),
                org_share_case_type_set_names,
            )
            print("org access case types:", len(org_access_case_type_ids))
            print("org share case types:", len(org_share_case_type_ids))
            print("reference data case type IDs:", len(expected_case_type_ids))

        return expected_case_type_ids

    # Note that this method is currently not used in the test, but it can be used for future more fine-grained tests that check ABAC filtering for operational data access,
    # instead of the current all-or-nothing approach for reference data access
    # It should test for access on case level, not just case type level, to verify that ABAC filtering is correctly applied for operational data access
    def _get_expected_case_type_ids_for_operational_data(
        self,
        env: Env,
        user: model.User,
    ) -> set[UUID]:
        """
        Determine the case type IDs that a user should have access to for operational data.

        This method calculates the union of case types accessible through either access rights
        or share rights. For each type of right (access/share), a user must satisfy BOTH
        organization-level and user-level policies to gain access to case types.

        Args:
            env (Env): The environment context for retrieving reference data
            user (model.User): The user for whom to determine accessible case type IDs

        Returns:
            set[UUID]: A set of case type IDs that the user should have operational access to

        Logic:
            1. Retrieves all relevant policies and case type set memberships
            2. For access rights:
               - Finds case type sets from organization access policies for user's org
               - Finds case type sets from user access policies for the specific user
               - Gets case types that are in BOTH org AND user accessible case type sets
            3. For share rights:
               - Finds case type sets from organization share policies for user's org
               - Finds case type sets from user share policies for the specific user
               - Gets case types that are in BOTH org AND user shareable case type sets
            4. Returns the union of case types accessible through either access OR share rights

        Note:
            - Access requires intersection of org AND user policies
            - Final result is union of access OR share case types
        """

        # Get all the reference data using cached methods
        all_organization_access_case_policies = (
            self._get_all_organization_access_case_policies(env)
        )
        all_organization_share_case_policies = (
            self._get_all_organization_share_case_policies(env)
        )
        all_user_access_case_policies = self._get_all_user_access_case_policies(env)
        all_user_share_case_policies = self._get_all_user_share_case_policies(env)
        all_case_type_set_members = self._get_all_case_type_set_members(env)

        # Get case type sets from organization access policies for this user's org
        org_access_case_type_set_ids = {
            x.case_type_set_id
            for x in all_organization_access_case_policies
            if x.organization_id == user.organization_id
        }

        # Get case type sets from user access policies for this user
        user_access_case_type_set_ids = {
            x.case_type_set_id
            for x in all_user_access_case_policies
            if x.user_id == user.id
        }

        # Get all case types accessible through organization access policies
        org_access_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in org_access_case_type_set_ids
        }

        # Get all case types accessible through user access policies
        user_access_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in user_access_case_type_set_ids
        }

        # Intersection: case types that are accessible through BOTH org AND user access policies
        access_case_type_ids = org_access_case_type_ids & user_access_case_type_ids

        # Get case type sets from organization share policies for this user's org
        org_share_case_type_set_ids = {
            x.case_type_set_id
            for x in all_organization_share_case_policies
            if x.organization_id == user.organization_id
        }

        # Get case type sets from user share policies for this user
        user_share_case_type_set_ids = {
            x.case_type_set_id
            for x in all_user_share_case_policies
            if x.user_id == user.id
        }

        # Get all case types accessible through organization share policies
        org_share_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in org_share_case_type_set_ids
        }

        # Get all case types accessible through user share policies
        user_share_case_type_ids = {
            x.case_type_id
            for x in all_case_type_set_members
            if x.case_type_set_id in user_share_case_type_set_ids
        }

        # Intersection: case types that are accessible through BOTH org AND user share policies
        share_case_type_ids = org_share_case_type_ids & user_share_case_type_ids

        # Union: case types accessible through either access OR share rights
        expected_case_type_ids = access_case_type_ids | share_case_type_ids

        if VERBOSE:
            all_case_type_sets = self._get_all_case_type_sets(env)
            case_type_set_name_map = {cts.id: cts.name for cts in all_case_type_sets}

            org_access_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in org_access_case_type_set_ids
            ]
            user_access_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in user_access_case_type_set_ids
            ]
            org_share_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in org_share_case_type_set_ids
            ]
            user_share_case_type_set_names = [
                case_type_set_name_map.get(cts_id, str(cts_id))
                for cts_id in user_share_case_type_set_ids
            ]

            print(
                "org access case type sets:",
                len(org_access_case_type_set_ids),
                org_access_case_type_set_names,
            )
            print(
                "user access case type sets:",
                len(user_access_case_type_set_ids),
                user_access_case_type_set_names,
            )
            print("org access case types:", len(org_access_case_type_ids))
            print("user access case types:", len(user_access_case_type_ids))
            print("access intersection case types:", len(access_case_type_ids))
            print(
                "org share case type sets:",
                len(org_share_case_type_set_ids),
                org_share_case_type_set_names,
            )
            print(
                "user share case type sets:",
                len(user_share_case_type_set_ids),
                user_share_case_type_set_names,
            )
            print("org share case types:", len(org_share_case_type_ids))
            print("user share case types:", len(user_share_case_type_ids))
            print("share intersection case types:", len(share_case_type_ids))
            print("final union case type IDs:", len(expected_case_type_ids))

        return expected_case_type_ids

    ## Add more fine-grained tests for case type access, e.g. with ABAC filtering, and not just all-or-nothing as in the current test
    def test_case_type(self, env: Env) -> None:
        """
        Test that case type access is correctly controlled by ABAC policies for reference data.

        This test verifies that users can only access case types they are authorized to see
        based on organization-level policies. For reference data, all users within the same
        organization see the same reference data.

        Access logic for reference data:
        - Organization access policies OR organization share policies (union) = accessible case types
        - User-level policies are NOT considered for reference data access
        - All users in the same organization have identical reference data access

        Users with GE_REFDATA_ADMIN role have access to all case types.

        :param env: Test environment with app context and test utilities
        :type env: Env
        """

        all_case_types = self._read_all(env, model.CaseType)

        assert (
            len(all_case_types) > 0
        ), "No case types found in the system, cannot test access control for case types"

        all_users = self._get_all_users(env)
        all_organizations = self._get_all_organizations(env)

        for user in all_users:

            case_types = self._read_all(env, model.CaseType, user=user, return_id=True)

            if VERBOSE:
                print("-------------")
                org_name = next(
                    (o.name for o in all_organizations if o.id == user.organization_id),
                    "Unknown",
                )
                print(f"user: {user.name}, organization_name: {org_name}")

            if self._has_role(env, user, RoleSet.GE_REFDATA_ADMIN):

                assert case_types == all_case_types

            else:
                # retrieve all unique case type IDs from the retrieved policies for the user in question
                expected_case_type_ids = (
                    self._get_expected_case_type_ids_for_reference_data(env, user)
                )

                # get actual case type IDs from the returned case types
                actual_case_type_ids: set[UUID] = set(case_types)  # type: ignore[assignment]

                # temporarily print the user and the actual vs expected case type IDs for debugging purposes
                if VERBOSE:
                    print(
                        f"user: {user.name} actual: {len(actual_case_type_ids)}, expected: {len(expected_case_type_ids)}"
                    )

                assert actual_case_type_ids == expected_case_type_ids, (
                    f"User {user.name} should have access to case types: {expected_case_type_ids}, "
                    f"but got: {actual_case_type_ids}"
                )

    # TODO: Add tests for all other refdata models

    # For testing with generated test data in another fixture:
    # Save all generated data as a pickle file
    # In case of stable set of data for testing => use pickle file instead of generating new data each time

    @pytest.mark.skip(reason="Skipped while developing other tests")
    def test_col(self, env: Env) -> None:
        all_cols = self._read_all(env, model.Col)
        for user in self._get_all_users(env):
            cols = self._read_all(env, model.Col, user=user)
            assert cols == all_cols

    def _get_expected_case_type_col_set_ids_for_reference_data(
        self,
        env: Env,
        user: model.User,
    ) -> set[UUID]:
        """
        Get expected CaseTypeColSet IDs for reference data access for a user.

        For reference data, the allowed CaseTypeColSet IDs are those referenced directly in the
        organization access and share policies for the user's organization.
        """
        all_org_access_policies: list[model.OrganizationAccessCasePolicy] = (
            self._get_all_organization_access_case_policies(env)
        )
        all_org_share_policies: list[model.OrganizationShareCasePolicy] = (
            self._get_all_organization_share_case_policies(env)
        )

        org_access_col_set_ids = {
            x.read_case_type_col_set_id
            for x in all_org_access_policies
            if x.organization_id == user.organization_id
            and x.read_case_type_col_set_id is not None
        }

        # For share policies, collect all from_data_collection Data Collection IDs shared with the user's organization
        org_share_data_collection_ids = {
            x.from_data_collection_id
            for x in all_org_share_policies
            if x.organization_id == user.organization_id
        }

        # Only include read_case_type_col_set_id from share policies where from_data_collection_id is in org_share_data_collection_ids
        org_share_col_set_ids = {
            x.read_case_type_col_set_id
            for x in all_org_access_policies
            if x.data_collection_id in org_share_data_collection_ids
            and x.read_case_type_col_set_id is not None
        }

        expected_case_type_col_set_ids = org_access_col_set_ids | org_share_col_set_ids

        return expected_case_type_col_set_ids

    # Note: test data do not currently include any reference data for case type columns set members
    # but this test can be used when such data is added
    def test_case_type_col_set(self, env: Env) -> None:

        all_organizations = self._get_all_organizations(env)
        all_col_set_ids: list[UUID] = self._read_all(env, model.CaseTypeColSet, return_id=True)  # type: ignore[assignment]

        for user in self._get_all_users(env):

            if VERBOSE:
                print("-------------")
                org_name = next(
                    (o.name for o in all_organizations if o.id == user.organization_id),
                    "Unknown",
                )
                print(f"user: {user.name}, organization_name: {org_name}")

            if self._has_role(env, user, RoleSet.GE_REFDATA_ADMIN):

                expected_case_type_col_set_ids: set[UUID] = all_col_set_ids
            else:
                expected_case_type_col_set_ids: set[UUID] = (
                    self._get_expected_case_type_col_set_ids_for_reference_data(
                        env, user
                    )
                )

            actual_col_set_ids: list[UUID] = self._read_all(env, model.CaseTypeColSet, user=user, return_id=True)  # type: ignore[assignment]

            if VERBOSE:
                print("all col_set_ids:", len(all_col_set_ids))
                print("expected col_sets:", len(expected_case_type_col_set_ids))
                print("actual col_sets:", len(actual_col_set_ids))

            # Optionally, assert that the user only sees the expected col sets
            assert sorted(actual_col_set_ids) == sorted(expected_case_type_col_set_ids)  # type: ignore[comparison-overlap]
