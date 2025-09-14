import abc
from collections.abc import Callable
from enum import Enum
from typing import Any, Type
from uuid import UUID

from gen_epix.commondb.domain.command import Command, OrganizationAdminPolicyCrudCommand
from gen_epix.commondbdb.domain.model import User
from gen_epix.commondbdb.domain.service import BaseAbacService
from gen_epix.fastapp.model import CrudCommand, Policy


class BaseIsOrganizationAdminPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        user_class: Type[User] = User,
        app_admin_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.user_class = user_class
        self.app_admin_roles = app_admin_roles or set()
        self.props = kwargs

    @abc.abstractmethod
    def register_retrieve_organization_ids_handler(
        self,
        command_class: Type[Command],
        handler: Callable[[Command], set[UUID]],
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_organization_ids(self, cmd: Command) -> set[UUID]:
        raise NotImplementedError


class BaseReadOrganizationResultsOnlyPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        exempt_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.exempt_roles = exempt_roles or set()
        self.props = kwargs


class BaseReadSelfResultsOnlyPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        exempt_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.exempt_roles = exempt_roles or set()
        self.props = kwargs


class BaseReadUserPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        root_role: Enum | None = None,
        app_admin_roles: set[Enum] | None = None,
        org_admin_roles: set[Enum] | None = None,
        organization_admin_policy_crud_command_class: Type[
            CrudCommand
        ] = OrganizationAdminPolicyCrudCommand,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.root_role = root_role
        self.app_admin_roles = app_admin_roles or set()
        self.org_admin_roles = org_admin_roles or set()
        self.organization_admin_policy_crud_command_class = (
            organization_admin_policy_crud_command_class
        )
        self.props = kwargs


class BaseUpdateUserPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        root_role: Enum | None = None,
        app_admin_roles: set[Enum] | None = None,
        org_admin_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.root_role = root_role
        self.app_admin_roles = app_admin_roles or set()
        self.org_admin_roles = org_admin_roles or set()
        self.props = kwargs
