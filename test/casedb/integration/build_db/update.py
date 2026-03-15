from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    ALL_USERS,
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_USERS,
    BELOW_ORG_ADMIN_USERS,
    BELOW_USER_ADMIN_USERS,
    ORG_ADMIN_OR_ABOVE_USERS,
    REFDATA_ADMIN_OR_ABOVE_USERS,
    ROOT,
    SKIP_CREATE_DATA,
    SKIP_RAISE,
)
from uuid import UUID

import pydantic
import pytest

from gen_epix.casedb.domain import enum, exc, model
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.enum import RoleSet as CommonRoleSet


@pytest.mark.scenario_ids(
    "TC-RBAC-01-14",
    "TC-RBAC-01-15",
    "TC-RBAC-02-09",
    "TC-RBAC-02-10",
    "TC-RBAC-02-11",
    "TC-RBAC-02-12",
    "TC-RBAC-02-05",
    "TC-RBAC-02-05",
    "TC-RBAC-02-06",
    "TC-RBAC-02-07",
    "TC-BIO-01-01",
    "TC-BIO-01-02",
    "TC-BIO-02-01",
    "TC-BIO-02-02",
    "TC-BIO-03-01",
    "TC-BIO-03-02",
    "TC-BIO-04-01",
    "TC-BIO-04-02",
)
class TestUpdate:
    # UPDATE tests

    def test_update_user(self, env: Env) -> None:
        org_id_name_map = {x.id: x.name for x in env.db[model.Organization].values()}
        is_not_restricted_roles = env.role_set_map[CommonRoleSet.GE_APP_ADMIN]
        if env.verbose:
            print("\nUser updates:")
        for role in sorted(env.role_set_map[CommonRoleSet.ALL]):
            user_str = f"{env.rev_role_map[role].name.lower()}1_1"
            user: model.User = env._get_obj(model.User, user_str)
            is_root = role == env.root_role
            is_not_restricted = role in is_not_restricted_roles
            org_admin_orgs = {
                org_id_name_map[x]
                for x in env.get_org_ids_for_org_admin(user, on_no_admin="return")
            }
            for tgt_role in sorted(env.role_set_map[CommonRoleSet.ALL]):
                token = env.rev_role_map[tgt_role].name.lower()
                tgt_users_str = [
                    f"{token}1_1",
                    f"{token}1_2",
                    f"{token}2_1",
                ]
                new_tgt_orgs = [f"org{i+1}" for i in range(0, 5)]
                is_sub_role = env.is_sub_role(tgt_role, role)
                if (
                    is_sub_role
                    and env.rev_role_map[tgt_role] == CommonRole.REFDATA_ADMIN
                    and env.rev_role_map[role] == CommonRole.ORG_ADMIN
                ):
                    # Special case where REFDATA_ADMIN and ORG_ADMIN have same permissions
                    # Occurs only for commondb
                    is_sub_role = False
                for tgt_user_str, new_tgt_org in zip(tgt_users_str, new_tgt_orgs):
                    tgt_user: model.User = env._get_obj(model.User, tgt_user_str)
                    tgt_org = org_id_name_map[tgt_user.organization_id]
                    # Determine if user can update tgt_user and also their tgt_org
                    is_self = user_str == tgt_user_str
                    is_update_allowed = False
                    is_org_update_allowed = False
                    if is_root:
                        # ROOT can update anyone
                        is_update_allowed = True
                        is_org_update_allowed = True
                    elif is_self:
                        # User cannot update themselves
                        pass
                    elif not is_sub_role:
                        # User cannot update someone with the same or more permissions
                        pass
                    elif is_not_restricted:
                        # APP_ADMIN and above user can update anyone with less permissions
                        is_update_allowed = True
                        is_org_update_allowed = True
                    elif tgt_org in org_admin_orgs:
                        # ORG_ADMIN user can update users in their organizations under admin but only if they have less permissions
                        is_update_allowed = True
                        is_org_update_allowed = new_tgt_org in org_admin_orgs
                    msg = f"{user.name}: {tgt_user_str} {tgt_org}->{new_tgt_org}"
                    if env.verbose:
                        print(msg)
                    # Test update
                    if is_update_allowed:
                        env.update_user(user, tgt_user, is_active=False)
                        env.update_user(user, tgt_user, is_active=True)
                    else:
                        with pytest.raises(exc.UnauthorizedAuthError):
                            env.update_user(user, tgt_user, is_active=False)
                        with pytest.raises(exc.UnauthorizedAuthError):
                            env.update_user(user, tgt_user, is_active=True)
                    if is_org_update_allowed:
                        env.update_user(user, tgt_user, organization_or_str=new_tgt_org)
                        env.update_user(user, tgt_user, organization_or_str=tgt_org)
                    else:
                        with pytest.raises(exc.UnauthorizedAuthError):
                            env.update_user(
                                user, tgt_user, organization_or_str=new_tgt_org
                            )
                    with pytest.raises(
                        (exc.UnauthorizedAuthError, exc.InvalidIdsError)
                    ):
                        env.update_user(user, tgt_user, set_dummy_organization=True)

    def test_update_user_role(self, env: Env) -> None:
        is_not_restricted_roles = env.role_set_map[CommonRoleSet.GE_APP_ADMIN]
        if env.verbose:
            print("\nUser role updates:")
        for role in sorted(env.role_set_map[CommonRoleSet.ALL]):
            user_str = f"{env.rev_role_map[role].name.lower()}1_1"
            user: model.User = env._get_obj(model.User, user_str)
            is_root = role == env.root_role
            is_not_restricted = role in is_not_restricted_roles
            org_admin_org_ids = env.get_org_ids_for_org_admin(
                user, on_no_admin="return"
            )
            for tgt_role in sorted(env.role_set_map[CommonRoleSet.ALL]):
                token = env.rev_role_map[tgt_role].name.lower()
                tgt_users_str = [
                    f"{token}1_1",
                    f"{token}2_1",
                ]
                is_sub_role = env.is_sub_role(tgt_role, role)
                if (
                    is_sub_role
                    and env.rev_role_map[tgt_role] == CommonRole.REFDATA_ADMIN
                    and env.rev_role_map[role] == CommonRole.ORG_ADMIN
                ):
                    # Special case where REFDATA_ADMIN and ORG_ADMIN have same permissions
                    # Occurs only for commondb
                    is_sub_role = False
                for tgt_user_str in tgt_users_str:
                    tgt_user: model.User = env._get_obj(model.User, tgt_user_str)
                    tgt_user_org_id = tgt_user.organization_id
                    if not SKIP_RAISE:
                        msg = f"{user_str}: {tgt_user_str} no roles"
                        if env.verbose:
                            print(msg)
                        with pytest.raises(
                            (
                                exc.UnauthorizedAuthError,
                                exc.InvalidArgumentsError,
                                pydantic.ValidationError,
                            )
                        ):
                            env.update_user(user, tgt_user, roles=set())
                    for tgt_extra_role in env.role_set_map[CommonRoleSet.ALL]:
                        # Determine if user can add tgt_extra_role to tgt_user
                        # The tgt_extra_role must have less permissions than the user's
                        # role unless the user is ROOT
                        is_self = user_str == tgt_user_str
                        is_extra_sub_role = env.is_sub_role(tgt_extra_role, role)
                        if (
                            is_extra_sub_role
                            and env.rev_role_map[tgt_extra_role]
                            == CommonRole.REFDATA_ADMIN
                            and env.rev_role_map[role] == CommonRole.ORG_ADMIN
                        ):
                            # Special case where REFDATA_ADMIN and ORG_ADMIN have same permissions
                            # Occurs only for commondb
                            is_extra_sub_role = False
                        is_allowed = False
                        if is_root:
                            # ROOT can update anyone
                            is_allowed = True
                        elif is_self:
                            # User cannot update themselves
                            pass
                        elif not is_sub_role or not is_extra_sub_role:
                            # User cannot update someone with the same or more permissions
                            pass
                        elif is_not_restricted:
                            # APP_ADMIN and above user can update anyone with less permissions
                            is_allowed = True
                        elif tgt_user_org_id in org_admin_org_ids:
                            # ORG_ADMIN user can update users in their organizations under admin
                            is_allowed = True
                        # Update tgt_user roles
                        tgt_roles = set(tgt_user.roles)
                        tgt_roles.add(tgt_extra_role)
                        msg = f"{user_str}: {tgt_user_str} + {tgt_extra_role}"
                        if env.verbose:
                            print(msg)
                        if is_allowed:
                            # Add and remove role again to have the same roles for the
                            # next iteration
                            env.update_user(user, tgt_user, roles=tgt_roles)
                            if len(tgt_roles) > 1:
                                tgt_roles.remove(tgt_extra_role)
                                env.update_user(user, tgt_user, roles=tgt_roles)
                        else:
                            if not SKIP_RAISE:
                                with pytest.raises(exc.UnauthorizedAuthError):
                                    env.update_user(user, tgt_user, roles=tgt_roles)

    def test_update_data_collection(self, env: Env) -> None:
        env.create_data_collection(ROOT, "data_collection99")
        for i, user in enumerate(APP_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.DataCollection, "data_collection99", {"description": str(i)}
            )
        env.delete_object(ROOT, model.DataCollection, "data_collection99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_data_collection_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.DataCollection,
                    "data_collection1",
                    {"description": str(-i)},
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_update_organization_access_case_policy(self, env: Env) -> None:
        # TODO: test update Organization, DataCollection, ColSet
        env.create_data_collection(ROOT, "data_collection99")
        name = "org_case_policy1_99"  # organization1, data_collection99, case_type_set1, col_set1
        organization_access_case_policy = env.create_organization_access_case_policy(
            ROOT,
            name,
            "case_type_set1",
            read_col_set="col_set1",
            write_col_set="col_set1",
        )
        for i, user in enumerate(APP_ADMIN_OR_ABOVE_USERS):
            # Alternate between write False and True to make sure a change is persisted
            env.update_object(
                user,
                model.OrganizationAccessCasePolicy,
                organization_access_case_policy,
                props={"write_case_set": bool(i % 2 != 0)},
            )
        if not SKIP_RAISE:
            for i, user in enumerate(["org_admin1_1"] + BELOW_USER_ADMIN_USERS):
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.update_object(
                        user,
                        model.OrganizationAccessCasePolicy,
                        organization_access_case_policy,
                        props={"write_case_set": bool(i % 2 != 0)},
                    )
        env.delete_object(
            ROOT, model.OrganizationAccessCasePolicy, organization_access_case_policy
        )
        env.delete_object(ROOT, model.DataCollection, "data_collection99")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_update_user_access_case_policy(self, env: Env) -> None:
        env.create_data_collection(ROOT, "data_collection99")
        name = "org_case_policy1_99"
        organization_access_case_policy = env.create_organization_access_case_policy(
            ROOT,
            "org_case_policy1_99",
            "case_type_set1",
            read_col_set="col_set1",
            write_col_set="col_set1",
        )
        args = {
            "data_collection": "data_collection99",
            "case_type_set": "case_type_set1",
        }
        kwargs = {
            "read_col_set": "col_set1",
            "write_col_set": "col_set1",
        }
        tgt_users = ["org_admin1_1", "org_user1_1"]
        for tgt_user in tgt_users:
            tgt_user = env._get_obj(model.User, tgt_user)
            user_access_case_policy = env.create_user_access_case_policy(
                "org_admin1_1", tgt_user, *list(args.values()), **kwargs
            )
            for i, user in enumerate(["org_admin1_1"]):
                # Alternate between write False and True to make sure a change is persisted
                env.update_object(
                    user,
                    model.UserAccessCasePolicy,
                    user_access_case_policy,
                    args
                    | kwargs
                    | {"user_id": tgt_user.id, "write_case_set": bool(i % 2 != 0)},
                )
            if not SKIP_RAISE:
                for i, user in enumerate(BELOW_USER_ADMIN_USERS):
                    with pytest.raises(exc.UnauthorizedAuthError):
                        env.update_object(
                            user,
                            model.UserAccessCasePolicy,
                            user_access_case_policy,
                            args
                            | kwargs
                            | {
                                "user_id": tgt_user.id,
                                "write_case_set": bool(i % 2 != 0),
                            },
                        )
            env.delete_object(ROOT, model.UserAccessCasePolicy, user_access_case_policy)
        env.delete_object(
            ROOT, model.OrganizationAccessCasePolicy, organization_access_case_policy
        )
        env.delete_object(ROOT, model.DataCollection, "data_collection99")

    def test_update_update_user_own_organization(self, env: Env) -> None:
        if env.verbose:
            print("\nTEMP User own organization update:")
        for role in sorted(env.role_set_map[CommonRoleSet.ALL]):
            # if role == CommonRole.ROOT:
            #     continue
            user_str = f"{env.rev_role_map[role].name.lower()}1_1"
            if env.verbose:
                print(f"User: {user_str} -> org2")
            user = env.update_user_own_organization(
                user_str, organization_or_str="org2"
            )
            if env.verbose:
                print(f"User: {user_str} -> org1")
            user = env.update_user_own_organization(user, organization_or_str="org1")
            if not SKIP_RAISE:
                if env.verbose:
                    print(f"User: {user_str} -> dummy")
                with pytest.raises(
                    (
                        exc.LinkConstraintViolationError,
                        exc.InvalidIdsError,
                        exc.InvalidLinkIdsError,
                    )
                ):
                    env.update_user_own_organization(user, set_dummy_organization=True)

    def test_update_dim(self, env: Env) -> None:
        env.create_ref_dim(ROOT, "dim99", enum.DimType.TEXT)
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(user, model.RefDim, "dim99", {"description": str(i)})
        env.delete_object(ROOT, model.RefDim, "dim99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_ref_dim_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.RefDim, "ref_dim1", {"description": str(-i)}
                )

    def test_update_ref_col(self, env: Env) -> None:
        env.create_ref_col(ROOT, "ref_col1_99")
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.RefCol, "ref_col1_99", {"description": str(i)}
            )
        env.delete_object(ROOT, model.RefCol, "ref_col1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_ref_col_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.RefCol, "ref_col1_1", {"description": str(-i)}
                )

    def test_update_case_type(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.CaseType, "case_type99", {"description": str(i)}
            )
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.CaseType, "case_type1", {"description": str(-i)}
                )

    def test_update_col(self, env: Env) -> None:
        env.create_ref_col(ROOT, "ref_col1_99")
        env.create_col(ROOT, "col1_1_1_99")
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.Col,
                "col1_1_1_99",
                {"description": str(i)},
            )
        env.delete_object(ROOT, model.Col, "col1_1_1_99")
        env.delete_object(ROOT, model.RefCol, "ref_col1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_col_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.Col,
                    "col1_1_1_1",
                    {"description": str(-i)},
                )

    def test_update_case_type_set_category(self, env: Env) -> None:
        env.create_case_type_set_category(ROOT, "case_type_set_category99")
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.CaseTypeSetCategory,
                "case_type_set_category99",
                {"description": str(i)},
            )
        env.delete_object(ROOT, model.CaseTypeSetCategory, "case_type_set_category99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_set_category_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.CaseTypeSetCategory,
                    "case_type_set_category1",
                    {"description": str(-i)},
                )

    def test_update_case_type_set(self, env: Env) -> None:
        env.create_case_type_set_category(ROOT, "case_type_set_category99")
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        env.create_case_type_set(
            ROOT, "case_type_set99", {"case_type99"}, "case_type_set_category99"
        )
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.CaseTypeSet, "case_type_set99", {"description": str(i)}
            )
        env.delete_object(ROOT, model.CaseTypeSet, "case_type_set99")
        env.delete_object(ROOT, model.CaseType, "case_type99")
        env.delete_object(ROOT, model.CaseTypeSetCategory, "case_type_set_category99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_set_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.CaseTypeSet, "case_type_set1", {"description": str(-i)}
                )

    def test_update_col_set(self, env: Env) -> None:
        env.create_col_set(ROOT, "col_set99", {"col1_1_1_1"})
        for i, user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.ColSet,
                "col_set99",
                {"description": str(i)},
            )
        env.delete_object(ROOT, model.ColSet, "col_set99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_col_set_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.ColSet,
                    "col_set1",
                    {"description": str(-i)},
                )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_col_set_member(self, env: Env) -> None:
        all_col_set_members: list[model.ColSetMember] = env.read_all(  # type: ignore[assignment]
            ROOT, model.ColSetMember
        )
        all_cols: list[model.Col] = env.read_all(ROOT, model.Col)  # type: ignore[assignment]
        col_case_type_map = {c.id: c.case_type_id for c in all_cols}
        for user in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(user)
            expected_member_ids = {
                x.id
                for x in all_col_set_members
                if col_case_type_map.get(x.col_id) in expected_case_type_ids
            }
            for member in expected_member_ids:
                member_obj = next(
                    (x for x in all_col_set_members if x.id == member),
                    None,
                )
                if user in APP_ADMIN_OR_ABOVE_USERS:
                    # Use the update_col_set_member method to update a single
                    # ColSetMember object in the database
                    env.update_col_set_member(user, member_obj)  # type: ignore[assignment]
                else:
                    # update_col_set_member checks via the CRUD command
                    # the RBAC/ABAC permissions and should raise an error
                    with pytest.raises(exc.UnauthorizedAuthError):
                        env.update_col_set_member(user, member_obj)  # type: ignore[assignment]

    def test_update_contact(self, env: Env) -> None:
        env.create_contact(ROOT, "contact1_1_99")
        for i, user in enumerate(ORG_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.Contact,
                "contact1_1_99",
                {"email": f"contact{i}@example.com"},
            )
        env.delete_object(ROOT, model.Contact, "contact1_1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_contact_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_ORG_ADMIN_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.Contact, "contact1_1_1", {"email": str(-i)}
                )

    def test_update_site(self, env: Env) -> None:
        env.create_site(ROOT, "site1_99")
        for i, user in enumerate(ORG_ADMIN_OR_ABOVE_USERS):
            env.update_object(user, model.Site, "site1_99", {"name": str(i)})
        env.delete_object(ROOT, model.Site, "site1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_site_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_ORG_ADMIN_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(user, model.Site, "site1_1", {"name": str(-i)})

    # def test_update_case_set(self, env: Env) -> None:
    #     # TODO
    #     pass

    # def test_update_case_set_raise(self, env: Env) -> None:
    #     # TODO
    #     pass
