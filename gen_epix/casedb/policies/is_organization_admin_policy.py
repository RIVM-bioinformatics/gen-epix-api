from enum import Enum
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.common.domain.service import BaseAbacService
from gen_epix.common.policies import (
    IsOrganizationAdminPolicy as CommonIsOrganizationAdminPolicy,
)
from gen_epix.fastapp import CrudOperation


class IsOrganizationAdminPolicy(CommonIsOrganizationAdminPolicy):

    def __init__(
        self,
        abac_service: BaseAbacService,
        no_abac_org_admin_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            user_class=model.User,
            no_abac_org_admin_roles=enum.RoleSet.GE_APP_ADMIN.value,  # type: ignore[arg-type]
            **kwargs,
        )
        f = self.register_retrieve_organization_ids_handler
        f(
            command.OrganizationAccessCasePolicyCrudCommand,
            self._get_organization_ids_for_organization_case_policy,
        )
        f(
            command.OrganizationShareCasePolicyCrudCommand,
            self._get_organization_ids_for_organization_case_policy,
        )
        f(
            command.UserAccessCasePolicyCrudCommand,
            self._get_organization_ids_for_user_case_policy,
        )
        f(
            command.UserShareCasePolicyCrudCommand,
            self._get_organization_ids_for_user_case_policy,
        )

    def _get_organization_ids_for_organization_case_policy(
        self,
        cmd: (
            command.OrganizationAccessCasePolicyCrudCommand
            | command.OrganizationShareCasePolicyCrudCommand
        ),
    ) -> set[UUID]:
        policies: list[model.OrganizationAccessCasePolicy] | list[model.OrganizationShareCasePolicy] = cmd.get_objs()  # type: ignore[assignment]
        return {x.organization_id for x in policies}

    def _get_organization_ids_for_user_case_policy(
        self,
        cmd: (
            command.UserAccessCasePolicyCrudCommand
            | command.UserShareCasePolicyCrudCommand
        ),
    ) -> set[UUID]:
        policies: list[model.UserAccessCasePolicy] | list[model.UserShareCasePolicy] = cmd.get_objs()  # type: ignore[assignment]
        users: list[model.User] = self.abac_service.app.handle(
            command.UserCrudCommand(
                user=cmd.user,
                objs=None,
                obj_ids=list(set(x.user_id for x in policies)),
                operation=CrudOperation.READ_SOME,
            )
        )
        return {x.organization_id for x in users}
