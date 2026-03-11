from __future__ import annotations

from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.casedb import policies as policies
from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.commondb.domain.enum import RoleSet as CommonRoleSet
from gen_epix.fastapp import CrudOperation, EventTiming
from gen_epix.fastapp.model import Command
from gen_epix.filter import (
    CompositeFilter,
    EqualsBooleanFilter,
    EqualsUuidFilter,
    LogicalOperator,
    UuidSetFilter,
)
from gen_epix.util import map_paired_elements


class AbacService(BaseAbacService):

    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = (
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
        command.OrganizationAccessCasePolicyCrudCommand,
        command.OrganizationShareCasePolicyCrudCommand,
    )

    def register_policies(
        self,
        organization_admin_write_commands: set[type[Command]] | None = None,
        read_user_commands: set[type[Command]] | None = None,
        update_user_commands: set[type[Command]] | None = None,
        read_organization_results_only_commands: set[type[Command]] | None = None,
        read_self_results_only_commands: set[type[Command]] | None = None,
    ) -> None:
        super().register_policies(
            organization_admin_write_commands=organization_admin_write_commands,
            read_user_commands=read_user_commands,
            update_user_commands=update_user_commands,
            read_organization_results_only_commands=read_organization_results_only_commands,
            read_self_results_only_commands=read_self_results_only_commands,
        )
        policy = policies.CaseAbacPolicy(self)
        f = self.app.register_policy
        for command_class in BaseAbacService.CASE_ABAC_COMMANDS:
            f(command_class, policy, EventTiming.DURING)

    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        if cmd.user is None or cmd.user.id is None:
            raise exc.UnauthorizedAuthError("Command has no user")
        user_id = cmd.user.id
        return self._get_case_abac_cached(user_id)

    def update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        """
        Behaviour:
        - Update User.organization
        - Create UserAccessCasePolicies for the user and their new organization, that
          are the union of all UserAccessCasePolicies for that organization. Analogous
          for UserShareCasePolicies.

        - Delete any OrganizationAdminPolicy for the user and their previous
          organization
        - Delete any UserAccessCasePolicy for the user and their previous organization.
          Analogous for UserShareCasePolicy.
        - Create UserAccessCasePolicies for the user and their new organization, one
          for each OrganizationAccessCasePolicy for the new organization combined with
          each CaseTypeSet and rights from the user's UserAccessCasePolicies from
          the previous organization. Analogous for OrganizationShareCasePolicy and
          UserShareCasePolicy.
        """
        if not self.app.get_feature_flag("update_own_organization"):
            raise exc.FeatureDisabledError("Updating own organization is disabled")

        is_new_user = cmd.is_new_user
        tgt_organization_id = cmd.organization_id
        assert cmd.user is not None
        user: model.User = cmd.user  # type: ignore[assignment]
        assert user.id is not None

        # Special case: new organization is same as current
        if user.organization_id == tgt_organization_id and not is_new_user:
            return user

        with self.repository.uow():
            # Get all current user access and share case policies
            user_access_case_policies: list[model.UserAccessCasePolicy] = (
                self.app.handle(
                    command.UserAccessCasePolicyCrudCommand(
                        user=user,
                        obj_ids=None,
                        operation=CrudOperation.READ_ALL,
                        query_filter=EqualsUuidFilter(
                            key="user_id",
                            value=user.id,
                        ),
                    )
                )
            )
            user_share_case_policies: list[model.UserShareCasePolicy] = self.app.handle(
                command.UserShareCasePolicyCrudCommand(
                    user=user,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    query_filter=EqualsUuidFilter(
                        key="user_id",
                        value=user.id,
                    ),
                )
            )
            # Get all target organization access and share case policies
            organization_access_case_policies: list[
                model.OrganizationAccessCasePolicy
            ] = self.app.handle(
                command.OrganizationAccessCasePolicyCrudCommand(
                    user=user,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    query_filter=EqualsUuidFilter(
                        key="organization_id",
                        value=tgt_organization_id,
                    ),
                )
            )
            organization_share_case_policies: list[
                model.OrganizationShareCasePolicy
            ] = self.app.handle(
                command.OrganizationShareCasePolicyCrudCommand(
                    user=user,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    query_filter=EqualsUuidFilter(
                        key="organization_id",
                        value=tgt_organization_id,
                    ),
                )
            )
            # Convert target organization policies to new user policies
            new_user_access_case_policies = [
                model.UserAccessCasePolicy(
                    user_id=user.id, **x.model_dump(exclude={"id"})
                )
                for x in organization_access_case_policies
            ]
            new_user_share_case_policies = [
                model.UserShareCasePolicy(
                    user_id=user.id, **x.model_dump(exclude={"id"})
                )
                for x in organization_share_case_policies
            ]
            # Delete the current user policies
            if user_access_case_policies:
                _ = self.app.handle(
                    command.UserAccessCasePolicyCrudCommand(
                        user=user,
                        obj_ids=[
                            x.id for x in user_access_case_policies  # type: ignore[misc]
                        ],
                        operation=CrudOperation.DELETE_SOME,
                    )
                )
            if user_share_case_policies:
                _ = self.app.handle(
                    command.UserShareCasePolicyCrudCommand(
                        user=user,
                        obj_ids=[
                            x.id for x in user_share_case_policies  # type: ignore[misc]
                        ],
                        operation=CrudOperation.DELETE_SOME,
                    )
                )
            # Store the new user policies
            new_user_access_case_policies = self.app.handle(
                command.UserAccessCasePolicyCrudCommand(
                    user=user,
                    objs=new_user_access_case_policies,  # type: ignore[arg-type]
                    operation=CrudOperation.CREATE_SOME,
                )
            )
            new_user_share_case_policies = self.app.handle(
                command.UserShareCasePolicyCrudCommand(
                    user=user,
                    objs=new_user_share_case_policies,  # type: ignore[arg-type]
                    operation=CrudOperation.CREATE_SOME,
                )
            )
            # Change the user organization
            updated_user = user.model_copy()
            updated_user.organization_id = tgt_organization_id
            user = self.app.handle(
                command.UserCrudCommand(
                    user=user,
                    objs=updated_user,
                    operation=CrudOperation.UPDATE_ONE,
                )
            )

        # Invalidate cache
        # TODO: develop general system for caching and cache invalidation
        self._get_user_by_id_cached.cache_clear()  # type: ignore[attr-defined]
        self._get_case_abac_cached.cache_clear()  # type: ignore[attr-defined]
        self._get_ref_data_access_cached.cache_clear()  # type: ignore[attr-defined]

        return user

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def _get_case_abac_cached(
        self,
        user_id: UUID,
    ) -> model.CaseAbac:
        user = self._get_user_by_id_cached(user_id)
        organization_id = user.organization_id
        # @ABAC: Special case: user has full access, defined as all active private data collection policies and all active organization access and share case policies
        is_full_access = not self.role_set_map[CommonRoleSet.GE_APP_ADMIN].isdisjoint(
            user.roles
        )
        if is_full_access:
            return model.CaseAbac(
                is_full_access=True,
                case_type_access_abacs={},
                case_type_share_abacs={},
            )
        # Get filters for all the policies
        organization_filter = CompositeFilter(
            filters=[
                EqualsBooleanFilter(key="is_active", value=True),
                EqualsUuidFilter(key="organization_id", value=organization_id),
            ],
            operator=LogicalOperator.AND,
        )
        user_filter = CompositeFilter(
            filters=[
                EqualsBooleanFilter(key="is_active", value=True),
                EqualsUuidFilter(key="user_id", value=user_id),
            ],
            operator=LogicalOperator.AND,
        )

        # Retrieve all the policies as well as the CaseTypeSetMembers and ColSetMembers
        with self.repository.uow() as uow:
            # Retrieve organization access and share case policies
            organization_access_case_policies: list[
                model.OrganizationAccessCasePolicy
            ] = self.repository.crud(  # type: ignore[assignment]
                uow,
                user_id=user_id,
                model_class=model.OrganizationAccessCasePolicy,
                objs=None,
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
                filter=organization_filter,
            )
            organization_share_case_policies: list[
                model.OrganizationShareCasePolicy
            ] = self.repository.crud(  # type: ignore[assignment]
                uow,
                user_id=user_id,
                model_class=model.OrganizationShareCasePolicy,
                objs=None,
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
                filter=organization_filter,
            )
            # Retrieve user access and share case policies
            user_access_case_policies: list[model.UserAccessCasePolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=user_id,
                    model_class=model.UserAccessCasePolicy,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=user_filter,
                )
            )
            user_share_case_policies: list[model.UserShareCasePolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=user_id,
                    model_class=model.UserShareCasePolicy,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=user_filter,
                )
            )
            # Retrieve Cols per CaseType
            col_map: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
                [
                    (x.case_type_id, x.id)
                    for x in self.app.handle(
                        command.ColCrudCommand(
                            user=user,
                            objs=None,
                            obj_ids=None,
                            operation=CrudOperation.READ_ALL,
                        ),
                    )
                ],
                as_set=True,
            )
            # Retrieve relevant CaseTypeSetMembers and ColSetMembers
            all_case_policies: list[
                model.OrganizationAccessCasePolicy
                | model.UserAccessCasePolicy
                | model.OrganizationShareCasePolicy
                | model.UserShareCasePolicy
            ] = (
                organization_access_case_policies
                + organization_share_case_policies
                + user_access_case_policies
                + user_share_case_policies
            )
            case_type_set_ids = frozenset(x.case_type_set_id for x in all_case_policies)
            case_type_set_member_map: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
                [
                    (x.case_type_set_id, x.case_type_id)
                    for x in self.app.handle(
                        command.CaseTypeSetMemberCrudCommand(
                            user=user,
                            objs=None,
                            obj_ids=None,
                            operation=CrudOperation.READ_ALL,
                            query_filter=UuidSetFilter(
                                key="case_type_set_id",
                                members=case_type_set_ids,
                            ),
                        ),
                    )
                ],
                as_set=True,
            )
            all_access_case_policies: list[
                model.OrganizationAccessCasePolicy | model.UserAccessCasePolicy
            ] = (organization_access_case_policies + user_access_case_policies)
            col_set_ids: set[UUID] = set(
                x.read_col_set_id for x in all_access_case_policies if x.read_col_set_id
            ) | set(
                x.write_col_set_id
                for x in all_access_case_policies
                if x.write_col_set_id
            )
            col_set_member_map: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
                [
                    (x.col_set_id, x.col_id)
                    for x in self.app.handle(
                        command.ColSetMemberCrudCommand(
                            user=user,
                            objs=None,
                            obj_ids=None,
                            operation=CrudOperation.READ_ALL,
                            query_filter=UuidSetFilter(
                                key="col_set_id",
                                members=frozenset(col_set_ids),
                            ),
                        ),
                    )
                ],
                as_set=True,
            )

        # Create and return the case abac object with the intersection of the rights
        return model.CaseAbac(
            is_full_access=is_full_access,
            case_type_access_abacs=AbacService._get_access_intersect(
                organization_access_case_policies,
                user_access_case_policies,
                case_type_set_member_map,
                col_map,
                col_set_member_map,
            ),
            case_type_share_abacs=AbacService._get_share_intersect(
                organization_share_case_policies,
                user_share_case_policies,
                case_type_set_member_map,
            ),
        )

    @staticmethod
    def _get_access_dict(
        case_policies: list[
            model.OrganizationAccessCasePolicy | model.UserAccessCasePolicy
        ],
        case_type_set_member_map: dict[UUID, set[UUID]],
        col_map: dict[UUID, set[UUID]],
        col_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeAccessAbac]]:
        def _get_col_ids(
            col_set_id: UUID | None,
        ) -> set[UUID]:
            return col_set_member_map.get(col_set_id, set()) if col_set_id else set()

        dict_: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = {}
        for x in case_policies:
            case_type_ids = case_type_set_member_map.get(x.case_type_set_id, set())
            is_private = (
                getattr(x, "is_private", True) if hasattr(x, "is_private") else True
            )
            # Create CaseTypeAccessAbac object for each CaseType id
            for case_type_id in case_type_ids:
                if case_type_id not in dict_:
                    dict_[case_type_id] = {}
                all_col_ids = col_map.get(case_type_id, set())
                case_type_access_abac = model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=x.data_collection_id,
                    is_private=is_private,
                    add_case=x.add_case,
                    remove_case=x.remove_case,
                    read_col_ids=all_col_ids & _get_col_ids(x.read_col_set_id),
                    write_col_ids=all_col_ids & _get_col_ids(x.write_col_set_id),
                    add_case_set=x.add_case_set,
                    remove_case_set=x.remove_case_set,
                    read_case_set=x.read_case_set,
                    write_case_set=x.write_case_set,
                )
                dict_[case_type_id][x.data_collection_id] = case_type_access_abac
        return dict_

    @staticmethod
    def _get_access_intersect(
        organization_access_case_policies: list[model.OrganizationAccessCasePolicy],
        user_access_case_policies: list[model.UserAccessCasePolicy],
        case_type_set_member_map: dict[UUID, set[UUID]],
        col_map: dict[UUID, set[UUID]],
        col_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeAccessAbac]]:
        dict1: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = (
            AbacService._get_access_dict(
                organization_access_case_policies,  # type: ignore[arg-type]
                case_type_set_member_map,
                col_map,
                col_set_member_map,
            )
        )
        dict2: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = (
            AbacService._get_access_dict(
                user_access_case_policies,  # type: ignore[arg-type]
                case_type_set_member_map,
                col_map,
                col_set_member_map,
            )
        )
        dict3: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = {}

        for case_type_id in set(dict1.keys()) & set(dict2.keys()):
            dict3[case_type_id] = {}
            data1 = dict1[case_type_id]
            data2 = dict2[case_type_id]
            for data_collection_id in set(data1.keys()) & set(data2.keys()):
                # Get both access case policies
                x = data1[data_collection_id]
                y = data2[data_collection_id]
                # Create the CaseType access abac object with the intersection of
                # the rights
                case_type_access_abac = model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=data_collection_id,
                    is_private=x.is_private and y.is_private,
                    add_case=x.add_case and y.add_case,
                    remove_case=x.remove_case and y.remove_case,
                    read_col_ids=x.read_col_ids & y.read_col_ids,
                    write_col_ids=x.write_col_ids & y.write_col_ids,
                    add_case_set=x.add_case_set and y.add_case_set,
                    remove_case_set=x.remove_case_set and y.remove_case_set,
                    read_case_set=x.read_case_set and y.read_case_set,
                    write_case_set=x.write_case_set and y.write_case_set,
                )
                # Add to dict only if any rights remain
                if not case_type_access_abac.has_any_rights():
                    continue
                dict3[case_type_id][data_collection_id] = case_type_access_abac
        return dict3

    @staticmethod
    def _get_share_dict(
        case_policies: list[
            model.OrganizationShareCasePolicy | model.UserShareCasePolicy
        ],
        case_type_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeShareAbac]]:
        dict_: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = {}
        for policy in case_policies:
            # Create CaseType share abac object for each CaseType id
            case_type_ids = case_type_set_member_map.get(policy.case_type_set_id, set())
            for case_type_id in case_type_ids:
                if case_type_id not in dict_:
                    dict_[case_type_id] = {}
                if policy.data_collection_id not in dict_[case_type_id]:
                    dict_[case_type_id][policy.data_collection_id] = (
                        model.CaseTypeShareAbac(
                            case_type_id=case_type_id,
                            data_collection_id=policy.data_collection_id,
                            add_case_from_data_collection_ids=set(),
                            remove_case_from_data_collection_ids=set(),
                            add_case_set_from_data_collection_ids=set(),
                            remove_case_set_from_data_collection_ids=set(),
                        )
                    )
                # Based on the policy, get the CaseTypeShareAbac object
                case_type_share_abac = dict_[case_type_id][policy.data_collection_id]
                case_type_share_abac = AbacService.get_case_type_share_abac_dict(
                    policy,
                    policy.data_collection_id,
                    policy.from_data_collection_id,
                    case_type_id,
                    case_type_share_abac,
                )
        return dict_

    @staticmethod
    def get_case_type_share_abac_dict(
        policy: model.OrganizationShareCasePolicy | model.UserShareCasePolicy,
        data_collection_id: UUID,
        from_data_collection_id: UUID,
        case_type_id: UUID,
        case_type_share_abac: model.CaseTypeShareAbac,
    ) -> model.CaseTypeShareAbac:
        if policy.add_case:
            case_type_share_abac.add_case_from_data_collection_ids.add(
                from_data_collection_id
            )
        if policy.remove_case:
            case_type_share_abac.remove_case_from_data_collection_ids.add(
                from_data_collection_id
            )
        if policy.add_case_set:
            case_type_share_abac.add_case_set_from_data_collection_ids.add(
                from_data_collection_id
            )
        if policy.remove_case_set:
            case_type_share_abac.remove_case_set_from_data_collection_ids.add(
                from_data_collection_id
            )

        return case_type_share_abac

    @staticmethod
    def _get_share_intersect(
        organization_share_case_policies: list[model.OrganizationShareCasePolicy],
        user_share_case_policies: list[model.UserShareCasePolicy],
        case_type_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeShareAbac]]:
        dict1: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = (
            AbacService._get_share_dict(
                organization_share_case_policies,  # type: ignore[arg-type]
                case_type_set_member_map,
            )
        )
        dict2: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = (
            AbacService._get_share_dict(
                user_share_case_policies,  # type: ignore[arg-type]
                case_type_set_member_map,
            )
        )
        dict3: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = {}

        for case_type_id in set(dict1.keys()) & set(dict2.keys()):
            dict3[case_type_id] = {}
            data1 = dict1[case_type_id]
            data2 = dict2[case_type_id]
            for data_collection_id in set(data1.keys()) & set(data2.keys()):
                # Get both share case policies
                x = dict1[case_type_id][data_collection_id]
                y = dict2[case_type_id][data_collection_id]
                # Create the CaseTypeShareAbac object with the intersection of the
                # rights
                dict3[case_type_id][data_collection_id] = model.CaseTypeShareAbac(
                    case_type_id=case_type_id,
                    data_collection_id=data_collection_id,
                    add_case_from_data_collection_ids=x.add_case_from_data_collection_ids
                    & y.add_case_from_data_collection_ids,
                    remove_case_from_data_collection_ids=x.remove_case_from_data_collection_ids
                    & y.remove_case_from_data_collection_ids,
                    add_case_set_from_data_collection_ids=x.add_case_set_from_data_collection_ids
                    & y.add_case_set_from_data_collection_ids,
                    remove_case_set_from_data_collection_ids=x.remove_case_set_from_data_collection_ids
                    & y.remove_case_set_from_data_collection_ids,
                )
        # Remove any CaseTypeShareAbac objects with no rights
        for case_type_id in dict3:
            to_pop_data_collection_ids = {
                x for x, y in dict3[case_type_id].items() if not y.has_any_rights()
            }
            for data_collection_id in to_pop_data_collection_ids:
                dict3[case_type_id].pop(data_collection_id)
        return dict3

    def get_ref_data_access(self, cmd: command.Command) -> model.RefDataAccess:
        user = cmd.user
        if user is None:
            return model.RefDataAccess(
                user_id=None,
                is_full_access=True,
                case_type_set_ids=set(),
                case_type_ids=set(),
                col_set_ids=set(),
                col_ids=set(),
                dim_ids=set(),
                ref_dim_ids=set(),
                ref_col_ids=set(),
            )
        return self._get_ref_data_access_cached(user)

    @cached(cache=TTLCache(maxsize=1024, ttl=300), key=lambda self, user: user.id)
    def _get_ref_data_access_cached(self, user: model.User) -> model.RefDataAccess:

        if not self.role_set_map[CommonRoleSet.GE_REFDATA_ADMIN].isdisjoint(user.roles):
            # REFDATA_ADMIN or above has full access, return unrestricted
            # (the is_full_access check in individual handlers will handle this)
            return model.RefDataAccess(
                user_id=user.id,
                is_full_access=True,
                case_type_set_ids=set(),
                case_type_ids=set(),
                col_set_ids=set(),
                col_ids=set(),
                dim_ids=set(),
                ref_dim_ids=set(),
                ref_col_ids=set(),
            )

        with self.repository.uow() as uow:
            # Determine applicable organisation(s)
            organization_ids: set[UUID] = {user.organization_id}
            if not self.role_set_map[CommonRoleSet.GE_ORG_ADMIN].isdisjoint(user.roles):
                # ORG_ADMIN (rest of roles handled earlier): add all organizations that this user is admin for
                organization_admin_policies: list[model.OrganizationAdminPolicy] = self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user.id,
                    self.organization_admin_policy_model_class,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsUuidFilter(key="user_id", value=user.id),
                            EqualsBooleanFilter(key="is_active", value=True),
                        ],
                    ),
                )
                organization_ids |= {
                    x.organization_id for x in organization_admin_policies
                }

            # Create filters for all the policies
            org_filter = CompositeFilter(
                filters=[
                    EqualsBooleanFilter(key="is_active", value=True),
                    UuidSetFilter(key="organization_id", members=organization_ids),
                ],
                operator=LogicalOperator.AND,
            )

            # Retrieve organization access and share case policies
            org_access_policies: list[model.OrganizationAccessCasePolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=None,
                    model_class=model.OrganizationAccessCasePolicy,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=org_filter,
                )
            )
            org_share_policies: list[model.OrganizationShareCasePolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=None,
                    model_class=model.OrganizationShareCasePolicy,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=org_filter,
                )
            )
            all_policies: list[
                model.OrganizationAccessCasePolicy | model.OrganizationShareCasePolicy
            ] = (org_access_policies + org_share_policies)

        # Collect CaseTypeSet and ColSet IDs from policies
        case_type_set_ids = {
            x.case_type_set_id for x in all_policies if x.case_type_set_id
        }
        col_set_ids = {
            x.read_col_set_id for x in org_access_policies if x.read_col_set_id
        } | {x.write_col_set_id for x in org_access_policies if x.write_col_set_id}

        # Retrieve all CaseTypeSetMembers and from there derive the CaseType IDs
        case_type_set_members: list[model.CaseTypeSetMember] = self.app.handle(
            command.CaseTypeSetMemberCrudCommand(
                user=user,
                objs=None,
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="case_type_set_id",
                    members=case_type_set_ids,
                ),
            )
        )
        case_type_ids: set[UUID] = {x.case_type_id for x in case_type_set_members}

        # Retrieve all ColSetMembers and from there derive the Col IDs
        col_set_members: list[model.ColSetMember] = self.app.handle(
            command.ColSetMemberCrudCommand(
                user=user,
                objs=None,
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="col_set_id",
                    members=col_set_ids,
                ),
            )
        )
        col_ids_from_sets: set[UUID] = {x.col_id for x in col_set_members}

        # Retrieve all Cols for the allowed CaseTypes, and derive the allowed cols and CaseType dims from that
        cols: list[model.Col] = self.app.handle(
            command.ColCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    filters=[
                        UuidSetFilter(key="case_type_id", members=case_type_ids),
                        UuidSetFilter(key="id", members=col_ids_from_sets),
                    ],
                    operator=LogicalOperator.AND,
                ),
            )
        )
        col_ids: set[UUID] = {x.id for x in cols if x.id is not None}
        dim_ids = {x.dim_id for x in cols}
        col_ids = {x.ref_col_id for x in cols}

        # Retrieve all dims for the allowed CaseType dims
        dims: list[model.Dim] = self.app.handle(
            command.DimCrudCommand(
                user=user,
                objs=None,
                obj_ids=list(dim_ids),
                operation=CrudOperation.READ_SOME,
            )
        )
        ref_dim_ids = {x.ref_dim_id for x in dims}

        return model.RefDataAccess(
            user_id=user.id,
            is_full_access=False,
            case_type_set_ids=case_type_set_ids,
            case_type_ids=case_type_ids,
            col_set_ids=col_set_ids,
            col_ids=col_ids,
            dim_ids=dim_ids,
            ref_dim_ids=ref_dim_ids,
            ref_col_ids=col_ids,
        )
