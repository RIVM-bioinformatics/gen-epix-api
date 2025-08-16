from __future__ import annotations

import logging
from typing import Any, Type
from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.casedb.policies.case_abac_policy import CaseAbacPolicy
from gen_epix.casedb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy,
)
from gen_epix.casedb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.casedb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy,
)
from gen_epix.casedb.policies.update_user_policy import UpdateUserPolicy
from gen_epix.common.util import map_paired_elements
from gen_epix.fastapp import App, CrudOperation, EventTiming
from gen_epix.fastapp.model import Command, CrudCommand, Policy
from gen_epix.filter import (
    BooleanOperator,
    CompositeFilter,
    EqualsBooleanFilter,
    EqualsUuidFilter,
    UuidSetFilter,
)


class AbacService(BaseAbacService):

    CACHE_INVALIDATION_COMMANDS: tuple[Type[Command], ...] = (
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
        command.OrganizationAccessCasePolicyCrudCommand,
        command.OrganizationShareCasePolicyCrudCommand,
    )

    def __init__(
        self,
        app: App,
        repository: BaseAbacRepository,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        super().__init__(app, repository=repository, logger=logger, **kwargs)
        self.repository: BaseAbacRepository

    def register_policies(self) -> None:
        f = self.app.register_policy
        policy: Policy
        command_class: Type[Command]
        policy = IsOrganizationAdminPolicy(self)
        for command_class in BaseAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS:
            f(command_class, policy, EventTiming.BEFORE)
        policy = UpdateUserPolicy(self)
        for command_class in BaseAbacService.UPDATE_USER_COMMANDS:
            f(command_class, policy, EventTiming.BEFORE)
        policy = CaseAbacPolicy(self)
        for command_class in BaseAbacService.CASE_ABAC_COMMANDS:
            f(command_class, policy, EventTiming.DURING)
        policy = ReadOrganizationResultsOnlyPolicy(self)
        for command_class in BaseAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS:
            f(command_class, policy, EventTiming.AFTER)
        policy = ReadSelfResultsOnlyPolicy(self)
        for command_class in BaseAbacService.READ_SELF_RESULTS_ONLY_COMMANDS:
            f(command_class, policy, EventTiming.AFTER)

    def crud(self, cmd: CrudCommand) -> Any:
        retval = super().crud(cmd)
        # Invalidate cache
        if issubclass(type(cmd), AbacService.CACHE_INVALIDATION_COMMANDS):
            self._get_user_by_id_cached.cache_clear()  # type:ignore[attr-defined]
            self._get_case_abac_cached.cache_clear()  # type:ignore[attr-defined]
        return retval

    def get_organizations_under_admin(self, user: model.User) -> set[UUID]:
        # TODO: inefficient implementation, retrieving first all objs and then filtering.
        # To be improved with e.g. CQS.
        with self.repository.uow() as uow:
            organization_admin_policies: list[
                model.OrganizationAdminPolicy
            ] = self.repository.crud(
                uow,
                user_id=user.id,
                model_class=model.OrganizationAdminPolicy,
                objs=None,
                obj_ids=None,
                operation=CrudOperation.READ_ALL,
            )  # type: ignore
        return set(
            x.organization_id
            for x in organization_admin_policies
            if x.user_id == user.id and x.is_active
        )

    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        if not isinstance(cmd.user, model.User):
            raise exc.ServiceException(
                "Command has no or wrong user type: {cmd.user.__class__.__name__}"
            )
        organization_admin_policies: list[model.OrganizationAdminPolicy] = (
            self.app.handle(
                command.OrganizationAdminPolicyCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.READ_ALL,
                )
            )
        )
        organization_admin_user_ids = {
            x.user_id
            for x in organization_admin_policies
            if x.organization_id == cmd.user.organization_id
        }
        users = self.app.handle(
            command.UserCrudCommand(
                user=cmd.user,
                obj_ids=list(organization_admin_user_ids),
                operation=CrudOperation.READ_SOME,
            )
        )
        return [
            model.UserNameEmail(
                id=x.id,
                name=x.name,
                email=x.email,
            )
            for x in users
        ]

    def temp_update_user_own_organization(
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
          each case type set and rights from the user's UserAccessCasePolicies from
          the previous organization. Analogous for OrganizationShareCasePolicy and
          UserShareCasePolicy.
        """
        user = cmd.user
        is_new_user = cmd.is_new_user
        tgt_organization_id = cmd.organization_id
        assert user is not None and user.id is not None
        user_id = user.id

        # Special case: new organization is same as current
        if user.organization_id == tgt_organization_id and not is_new_user:
            return user

        with self.repository.uow() as uow:
            # Get all current user access and share case policies
            user_access_case_policies: list[model.UserAccessCasePolicy] = (
                self.app.handle(
                    command.UserAccessCasePolicyCrudCommand(
                        user=user,
                        obj_ids=None,
                        operation=CrudOperation.READ_ALL,
                        query_filter=EqualsUuidFilter(
                            key="user_id",
                            value=user_id,
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
                        value=user_id,
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
                    user_id=user_id, **x.model_dump(exclude={"id"})
                )
                for x in organization_access_case_policies
            ]
            new_user_share_case_policies = [
                model.UserShareCasePolicy(
                    user_id=user_id, **x.model_dump(exclude={"id"})
                )
                for x in organization_share_case_policies
            ]
            # Delete the current user policies
            if user_access_case_policies:
                _ = self.app.handle(
                    command.UserAccessCasePolicyCrudCommand(
                        user=user,
                        obj_ids=[
                            x.id for x in user_access_case_policies  # type:ignore[misc]
                        ],
                        operation=CrudOperation.DELETE_SOME,
                    )
                )
            if user_share_case_policies:
                _ = self.app.handle(
                    command.UserShareCasePolicyCrudCommand(
                        user=user,
                        obj_ids=[
                            x.id for x in user_share_case_policies  # type:ignore[misc]
                        ],
                        operation=CrudOperation.DELETE_SOME,
                    )
                )
            # Store the new user policies
            new_user_access_case_policies = self.app.handle(
                command.UserAccessCasePolicyCrudCommand(
                    user=user,
                    objs=new_user_access_case_policies,  # type:ignore[arg-type]
                    operation=CrudOperation.CREATE_SOME,
                )
            )
            new_user_share_case_policies = self.app.handle(
                command.UserShareCasePolicyCrudCommand(
                    user=user,
                    objs=new_user_share_case_policies,  # type:ignore[arg-type]
                    operation=CrudOperation.CREATE_SOME,
                )
            )
            # Change the user organization
            user.organization_id = tgt_organization_id
            user = self.app.handle(
                command.UserCrudCommand(
                    user=user,
                    objs=user,
                    operation=CrudOperation.UPDATE_ONE,
                )
            )

        # Invalidate cache
        self._get_user_by_id_cached.cache_clear()
        self._get_case_abac_cached.cache_clear()

        return user

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def _get_user_by_id_cached(self, user_id: UUID) -> model.User:
        user: model.User = self.app.handle(  # type:ignore[assignment]
            command.UserCrudCommand(
                user=None,
                obj_ids=user_id,
                operation=CrudOperation.READ_ONE,
            )
        )
        return user

    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        if cmd.user is None or cmd.user.id is None:
            raise exc.UnauthorizedAuthError("Command has no user")
        user_id = cmd.user.id
        return self._get_case_abac_cached(user_id)

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def _get_case_abac_cached(
        self,
        user_id: UUID,
    ) -> model.CaseAbac:
        user = self._get_user_by_id_cached(user_id)
        organization_id = user.organization_id
        # @ABAC: Special case: user has full access, defined as all active private data collection policies and all active organization access and share case policies
        is_full_access = not enum.RoleSet.GE_APP_ADMIN.value.isdisjoint(user.roles)
        if is_full_access:
            return model.CaseAbac(
                is_full_access=True,
                private_data_collection_ids=set(),
                case_type_access_abacs={},
                case_type_share_abacs={},
            )
        # Get filters for all the policies
        organization_filter = CompositeFilter(
            filters=[
                EqualsBooleanFilter(key="is_active", value=True),
                EqualsUuidFilter(key="organization_id", value=organization_id),
            ],
            operator=BooleanOperator.AND,
        )
        user_filter = CompositeFilter(
            filters=[
                EqualsBooleanFilter(key="is_active", value=True),
                EqualsUuidFilter(key="user_id", value=user_id),
            ],
            operator=BooleanOperator.AND,
        )

        # Retrieve all the policies as well as the case type set members and case type col set members
        with self.repository.uow() as uow:
            # Retrieve organization access and share case policies
            organization_access_case_policies: list[
                model.OrganizationAccessCasePolicy
            ] = self.repository.crud(  # type:ignore[assignment]
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
            ] = self.repository.crud(  # type:ignore[assignment]
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
                self.repository.crud(  # type:ignore[assignment]
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
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    user_id=user_id,
                    model_class=model.UserShareCasePolicy,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=user_filter,
                )
            )
            # Retrieve case type cols per case type
            case_type_col_map: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
                [
                    (x.case_type_id, x.id)
                    for x in self.app.handle(
                        command.CaseTypeColCrudCommand(
                            user=user,
                            objs=None,
                            obj_ids=None,
                            operation=CrudOperation.READ_ALL,
                        ),
                    )
                ],
                as_set=True,
            )
            # Retrieve relevant case type set members and case type col set members
            all_case_policies: list[model.BaseCasePolicy] = (
                organization_access_case_policies  # type:ignore[assignment]
                + organization_share_case_policies
                + user_access_case_policies
                + user_share_case_policies  # type:ignore[operator]
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
            case_type_col_set_ids: set[UUID] = set(
                x.read_case_type_col_set_id
                for x in all_access_case_policies
                if x.read_case_type_col_set_id
            ) | set(
                x.write_case_type_col_set_id
                for x in all_access_case_policies
                if x.write_case_type_col_set_id
            )
            case_type_col_set_member_map: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
                [
                    (x.case_type_col_set_id, x.case_type_col_id)
                    for x in self.app.handle(
                        command.CaseTypeColSetMemberCrudCommand(
                            user=user,
                            objs=None,
                            obj_ids=None,
                            operation=CrudOperation.READ_ALL,
                            query_filter=UuidSetFilter(
                                key="case_type_col_set_id",
                                members=frozenset(case_type_col_set_ids),
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
                case_type_col_map,
                case_type_col_set_member_map,
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
        case_type_col_map: dict[UUID, set[UUID]],
        case_type_col_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeAccessAbac]]:
        def _get_case_type_col_ids(
            case_type_col_set_id: UUID | None,
        ) -> set[UUID]:
            return (
                case_type_col_set_member_map.get(case_type_col_set_id, set())
                if case_type_col_set_id
                else set()
            )

        dict_: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = {}
        for x in case_policies:
            case_type_ids = case_type_set_member_map.get(x.case_type_set_id, set())
            is_private = (
                getattr(x, "is_private", True) if hasattr(x, "is_private") else True
            )
            # Create case type access abac object for each case type id
            for case_type_id in case_type_ids:
                if case_type_id not in dict_:
                    dict_[case_type_id] = {}
                all_case_type_col_ids = case_type_col_map[case_type_id]
                case_type_access_abac = model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=x.data_collection_id,
                    is_private=is_private,
                    add_case=x.add_case,
                    remove_case=x.remove_case,
                    read_case_type_col_ids=all_case_type_col_ids
                    & _get_case_type_col_ids(x.read_case_type_col_set_id),
                    write_case_type_col_ids=all_case_type_col_ids
                    & _get_case_type_col_ids(x.write_case_type_col_set_id),
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
        case_type_col_map: dict[UUID, set[UUID]],
        case_type_col_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeAccessAbac]]:
        dict1: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = (
            AbacService._get_access_dict(
                organization_access_case_policies,  # type:ignore[arg-type]
                case_type_set_member_map,
                case_type_col_map,
                case_type_col_set_member_map,
            )
        )
        dict2: dict[UUID, dict[UUID, model.CaseTypeAccessAbac]] = (
            AbacService._get_access_dict(
                user_access_case_policies,  # type:ignore[arg-type]
                case_type_set_member_map,
                case_type_col_map,
                case_type_col_set_member_map,
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
                # Create the case type access abac object with the intersection of
                # the rights
                case_type_access_abac = model.CaseTypeAccessAbac(
                    case_type_id=case_type_id,
                    data_collection_id=data_collection_id,
                    is_private=x.is_private and y.is_private,
                    add_case=x.add_case and y.add_case,
                    remove_case=x.remove_case and y.remove_case,
                    read_case_type_col_ids=x.read_case_type_col_ids
                    & y.read_case_type_col_ids,
                    write_case_type_col_ids=x.write_case_type_col_ids
                    & y.write_case_type_col_ids,
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
        for x in case_policies:
            # Create case type share abac object for each case type id
            data_collection_id = x.data_collection_id
            from_data_collection_id = x.from_data_collection_id
            case_type_ids = case_type_set_member_map.get(x.case_type_set_id, set())
            for case_type_id in case_type_ids:
                if case_type_id not in dict_:
                    dict_[case_type_id] = {}
                if data_collection_id not in dict_[case_type_id]:
                    dict_[case_type_id][data_collection_id] = model.CaseTypeShareAbac(
                        case_type_id=case_type_id,
                        data_collection_id=data_collection_id,
                        add_case_from_data_collection_ids=set(),
                        remove_case_from_data_collection_ids=set(),
                        add_case_set_from_data_collection_ids=set(),
                        remove_case_set_from_data_collection_ids=set(),
                    )
                case_type_share_abac = dict_[case_type_id][data_collection_id]
                # Add the source data collection id to the appropriate sets
                if x.add_case:
                    case_type_share_abac.add_case_from_data_collection_ids.add(
                        from_data_collection_id
                    )
                if x.remove_case:
                    case_type_share_abac.remove_case_from_data_collection_ids.add(
                        from_data_collection_id
                    )
                if x.add_case_set:
                    case_type_share_abac.add_case_set_from_data_collection_ids.add(
                        from_data_collection_id
                    )
                if x.remove_case_set:
                    case_type_share_abac.remove_case_set_from_data_collection_ids.add(
                        from_data_collection_id
                    )
        return dict_

    @staticmethod
    def _get_share_intersect(
        organization_share_case_policies: list[model.OrganizationShareCasePolicy],
        user_share_case_policies: list[model.UserShareCasePolicy],
        case_type_set_member_map: dict[UUID, set[UUID]],
    ) -> dict[UUID, dict[UUID, model.CaseTypeShareAbac]]:
        dict1: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = (
            AbacService._get_share_dict(
                organization_share_case_policies,  # type:ignore[arg-type]
                case_type_set_member_map,
            )
        )
        dict2: dict[UUID, dict[UUID, model.CaseTypeShareAbac]] = (
            AbacService._get_share_dict(
                user_share_case_policies,  # type:ignore[arg-type]
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
                # Create the case type share abac object with the intersection of the
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
        # Remove any case type share abac objects with no rights
        for case_type_id in dict3:
            to_pop_data_collection_ids = {
                x for x, y in dict3[case_type_id].items() if not y.has_any_rights()
            }
            for data_collection_id in to_pop_data_collection_ids:
                dict3[case_type_id].pop(data_collection_id)
        return dict3
