from __future__ import annotations

from typing import Any, Type
from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.commondb import policies as policies
from gen_epix.commondb.domain import command, enum, exc, model
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.model import Command, CrudCommand
from gen_epix.filter import (
    CompositeFilter,
    EqualsBooleanFilter,
    EqualsUuidFilter,
    LogicalOperator,
)


class AbacService(BaseAbacService):

    CACHE_INVALIDATION_COMMANDS: tuple[Type[Command], ...] = tuple()

    def crud(self, cmd: CrudCommand) -> Any:
        retval = super().crud(cmd)
        # Invalidate cache
        if issubclass(type(cmd), AbacService.CACHE_INVALIDATION_COMMANDS):
            self._get_user_by_id_cached.cache_clear()  # type:ignore[attr-defined]
        return retval

    def retrieve_organizations_under_admin(
        self, cmd: command.RetrieveOrganizationsUnderAdminCommand
    ) -> set[UUID]:
        assert cmd.user and cmd.user.id
        # Special case: user has a role that makes them admin of all organizations
        is_all_organizations = False
        for policy in cmd._policies:
            if isinstance(policy, ReadOrganizationResultsOnlyPolicy):
                is_all_organizations = (
                    len(
                        cmd.user.roles.intersection(
                            policy.role_set_map[enum.RoleSet.GE_APP_ADMIN]
                        )
                    )
                    > 0
                )
                break
        if is_all_organizations:
            organizations: list[model.Organization] = self.app.handle(
                command.OrganizationCrudCommand(
                    user=cmd.user,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                )
            )
            return {x.id for x in organizations}  # type: ignore[misc]
        # Retrieve organizations for which the user is an admin
        with self.repository.uow() as uow:
            organization_admin_policies: list[model.OrganizationAdminPolicy] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    user_id=cmd.user.id,
                    model_class=self.organization_admin_policy_model_class,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsUuidFilter(key="user_id", value=cmd.user.id),
                            EqualsBooleanFilter(key="is_active", value=True),
                        ],
                    ),
                )
            )
        return set(x.organization_id for x in organization_admin_policies)

    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        if not isinstance(cmd.user, model.User):
            raise exc.ServiceException(
                "Command has no or wrong user type: {cmd.user.__class__.__name__}"
            )
        with self.repository.uow() as uow:
            organization_admin_policies: list[model.OrganizationAdminPolicy] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    user_id=cmd.user.id,
                    model_class=self.organization_admin_policy_model_class,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=EqualsUuidFilter(
                        key="organization_id", value=cmd.user.organization_id
                    ),
                )
            )
        organization_admin_user_ids = {
            x.user_id
            for x in organization_admin_policies
            if x.organization_id == cmd.user.organization_id and x.is_active
        }
        users = self.app.handle(
            self.user_crud_command_class(
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

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def _get_user_by_id_cached(self, user_id: UUID) -> model.User:
        user: model.User = self.app.handle(
            self.user_crud_command_class(
                user=None,
                obj_ids=user_id,
                operation=CrudOperation.READ_ONE,
            )
        )
        return user
