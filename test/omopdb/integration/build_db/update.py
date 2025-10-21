from test.seqdb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_USERS,
    SKIP_RAISE,
)

import pydantic
import pytest

from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.omopdb.domain import enum, exc, model


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
                            (
                                exc.UnauthorizedAuthError,
                                exc.InvalidArgumentsError,
                                pydantic.ValidationError,
                            )
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
