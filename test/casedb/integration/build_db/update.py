from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_USERS,
    BELOW_USER_ADMIN_USERS,
    METADATA_ADMIN_OR_ABOVE_USERS,
    ROOT,
    SKIP_CREATE_DATA,
    SKIP_RAISE,
)

import pytest

from gen_epix.casedb.domain import enum, exc, model


class TestUpdate:
    # UPDATE tests

    def test_update_user(self, env: Env) -> None:
        org_id_name_map = {x.id: x.name for x in env.db[model.Organization].values()}
        is_not_restricted_roles = enum.RoleSet.GE_APP_ADMIN.value
        if env.verbose:
            print("\nUser updates:")
        for role in sorted(enum.RoleSet.ALL.value, key=lambda x: x.value):
            role_str = role.value.lower()
            user_str = f"{role_str}1_1"
            user = env._get_obj(model.User, user_str)
            is_root = role == enum.Role.ROOT
            is_not_restricted = role in is_not_restricted_roles
            org_admin_orgs = {
                org_id_name_map[x]
                for x in env.get_org_ids_for_org_admin(user, on_no_admin="return")
            }
            for tgt_role in sorted(enum.RoleSet.ALL.value, key=lambda x: x.value):
                tgt_role_str = tgt_role.value.lower()
                tgt_users_str = [
                    f"{tgt_role_str}1_1",
                    f"{tgt_role_str}1_2",
                    f"{tgt_role_str}2_1",
                ]
                new_tgt_orgs = [f"org{i+1}" for i in range(0, 5)]
                is_sub_role = tgt_role in env.role_hierarchy[role]
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
                        # ORG_ADMIN user can update users in their organizations under admin
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
                        env.update_user(user, tgt_user, organization=new_tgt_org)
                        env.update_user(user, tgt_user, organization=tgt_org)
                    else:
                        with pytest.raises(exc.UnauthorizedAuthError):
                            env.update_user(user, tgt_user, organization=new_tgt_org)
                    with pytest.raises(
                        (exc.UnauthorizedAuthError, exc.InvalidIdsError)
                    ):
                        env.update_user(user, tgt_user, set_dummy_organization=True)

    def test_update_user_role(self, env: Env) -> None:
        is_not_restricted_roles = enum.RoleSet.GE_APP_ADMIN.value
        if env.verbose:
            print("\nUser role updates:")
        for role in sorted(enum.RoleSet.ALL.value, key=lambda x: x.value):
            role_str = role.value.lower()
            user_str = f"{role_str}1_1"
            user = env._get_obj(model.User, user_str)
            is_root = role == enum.Role.ROOT
            is_not_restricted = role in is_not_restricted_roles
            org_admin_org_ids = env.get_org_ids_for_org_admin(
                user, on_no_admin="return"
            )
            for tgt_role in sorted(enum.RoleSet.ALL.value, key=lambda x: x.value):
                tgt_role_str = tgt_role.value.lower()
                tgt_users_str = [
                    f"{tgt_role_str}1_1",
                    f"{tgt_role_str}2_1",
                ]
                is_sub_role = tgt_role in env.role_hierarchy[role]
                for tgt_user_str in tgt_users_str:
                    tgt_user = env._get_obj(model.User, tgt_user_str)
                    tgt_user_org_id = tgt_user.organization_id
                    if not SKIP_RAISE:
                        msg = f"{user_str}: {tgt_user_str} no roles"
                        if env.verbose:
                            print(msg)
                        with pytest.raises(
                            (exc.UnauthorizedAuthError, exc.InvalidArgumentsError)
                        ):
                            env.update_user(user, tgt_user, roles=set())
                    for tgt_extra_role in enum.RoleSet.ALL.value:
                        # Determine if user can add tgt_extra_role to tgt_user
                        # The tgt_extra_role must have less permissions than the user's
                        # role unless the user is ROOT
                        is_self = user_str == tgt_user_str
                        is_extra_sub_role = tgt_extra_role in env.role_hierarchy[role]
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
                        tgt_extra_role_str = tgt_extra_role.value
                        msg = f"{user_str}: {tgt_user_str} + {tgt_extra_role_str}"
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

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_update_organization_access_case_policy(self, env: Env) -> None:
        # TODO: test update organization, data collection, case type col set
        env.create_data_collection("root1_1", "data_collection21")
        name = "org_case_policy1_21"  # organization1, data_collection21, case_type_set1, case_type_col_set1
        organization_access_case_policy = env.create_organization_access_case_policy(
            "app_admin1_1",
            name,
            "case_type_set1",
            read_case_type_col_set="case_type_col_set1",
            write_case_type_col_set="case_type_col_set1",
        )
        for i, user in enumerate(["root1_1", "app_admin1_1"]):
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

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_update_user_access_case_policy(self, env: Env) -> None:
        env.create_data_collection("root1_1", "data_collection22")
        org_case_policy = "org_case_policy1_22"
        env.create_organization_access_case_policy(
            "app_admin1_1",
            org_case_policy,
            "case_type_set1",
            read_case_type_col_set="case_type_col_set1",
            write_case_type_col_set="case_type_col_set1",
        )
        args = {
            "data_collection": "data_collection22",
            "case_type_set": "case_type_set1",
        }
        kwargs = {
            "read_case_type_col_set": "case_type_col_set1",
            "write_case_type_col_set": "case_type_col_set1",
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

    def test_update_temp_update_user_own_organization(self, env: Env) -> None:
        if env.verbose:
            print("\nTEMP User own organization update:")
        for role in enum.RoleSet.ALL.value:
            # if role == enum.Role.ROOT:
            #     continue
            role_str = role.value.lower()
            user = f"{role_str}1_1"
            if env.verbose:
                print(f"User: {user} -> org2")
            user = env.temp_update_user_own_organization(user, organization="org2")
            if env.verbose:
                print(f"User: {user} -> org1")
            user = env.temp_update_user_own_organization(user, organization="org1")
            if not SKIP_RAISE:
                if env.verbose:
                    print(f"User: {user} -> dummy")
                with pytest.raises(
                    (
                        exc.LinkConstraintViolationError,
                        exc.InvalidIdsError,
                        exc.InvalidLinkIdsError,
                    )
                ):
                    env.temp_update_user_own_organization(
                        user, set_dummy_organization=True
                    )

    def test_update_data_collection(self, env: Env) -> None:
        env.create_data_collection("root1_1", "data_collection23")
        for i, user in enumerate(APP_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.DataCollection, "data_collection23", {"description": str(i)}
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_data_collection_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.DataCollection,
                    "data_collection23",
                    {"description": str(-i)},
                )

    def test_update_dim(self, env: Env) -> None:
        env.create_dim("root1_1", "text21", enum.DimType.TEXT)
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(user, model.Dim, "text21", {"description": str(i)})

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_dim_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(user, model.Dim, "text21", {"description": str(-i)})

    def test_update_col(self, env: Env) -> None:
        env.create_col("root1_1", "text21_1_text", enum.ColType.TEXT)
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(user, model.Col, "text21_1_text", {"description": str(i)})

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_col_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.Col, "text21_1_text", {"description": str(-i)}
                )

    def test_update_case_type(self, env: Env) -> None:
        env.create_case_type("root1_1", "case_type21", "disease1", "etiological_agent1")
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.CaseType, "case_type21", {"description": str(i)}
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.CaseType, "case_type21", {"description": str(-i)}
                )

    def test_update_case_type_col(self, env: Env) -> None:
        env.create_case_type_col("root1_1", "case_type21_text21_1_text")
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.CaseTypeCol,
                "case_type21_text21_1_text",
                {"description": str(i)},
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_col_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.CaseTypeCol,
                    "case_type21_text21_1_text",
                    {"description": str(-i)},
                )

    def test_update_case_type_set_category(self, env: Env) -> None:
        env.create_case_type_set_category("root1_1", "case_type_set_category21")
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.CaseTypeSetCategory,
                "case_type_set_category21",
                {"description": str(i)},
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_set_category_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.CaseTypeSetCategory,
                    "case_type_set_category21",
                    {"description": str(-i)},
                )

    def test_update_case_type_set(self, env: Env) -> None:
        env.create_case_type("root1_1", "case_type41", "disease1", "etiological_agent1")
        env.create_case_type_set(
            "root1_1", "case_type_set41", {"case_type41"}, "case_type_set_category21"
        )
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user, model.CaseTypeSet, "case_type_set41", {"description": str(i)}
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_set_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user, model.CaseTypeSet, "case_type_set41", {"description": str(-i)}
                )

    def test_update_case_type_col_set(self, env: Env) -> None:
        env.create_case_type_col_set(
            "root1_1", "case_type_col_set31", {"case_type21_text21_1_text"}
        )
        for i, user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            env.update_object(
                user,
                model.CaseTypeColSet,
                "case_type_col_set31",
                {"description": str(i)},
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_update_case_type_col_set_raise(self, env: Env) -> None:
        for i, user in enumerate(BELOW_APP_ADMIN_DATA_USERS):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_object(
                    user,
                    model.CaseTypeColSet,
                    "case_type_col_set31",
                    {"description": str(-i)},
                )

    @pytest.mark.skip(
        reason="To be adjusted to similar structure as e.g test_update_case_type_col_set_member"
    )
    def test_update_case_type_col_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -
        """
        all_case_type_col_set_members = env.read_all(ROOT, model.CaseTypeColSetMember)
        for user in METADATA_ADMIN_OR_ABOVE_USERS:
            env.update_case_type_col_set_member(user, all_case_type_col_set_members[-1])

    @pytest.mark.skip(
        reason="To be adjusted to similar structure as e.g test_update_case_type_col_set_member"
    )
    def test_update_case_type_col_set_member_raise(self, env: Env) -> None:
        all_case_type_col_set_members = env.read_all(ROOT, model.CaseTypeColSetMember)
        for user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.update_case_type_col_set_member(
                    user, all_case_type_col_set_members[-1]
                )

    # def test_update_case_set(self, env: Env) -> None:
    #     # TODO
    #     pass

    # def test_update_case_set_raise(self, env: Env) -> None:
    #     # TODO
    #     pass
