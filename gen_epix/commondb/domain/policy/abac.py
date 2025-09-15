import abc
from collections.abc import Callable
from enum import Enum
from typing import Any, Type
from uuid import UUID

from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.command import Command, OrganizationAdminPolicyCrudCommand
from gen_epix.commondb.domain.model import User
from gen_epix.commondb.domain.policy.util import get_role_set_map
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp.model import CrudCommand, Policy


class BaseIsOrganizationAdminPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        role_map: dict[Enum, Enum] | None = None,
        user_class: Type[User] = User,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.user_class = user_class
        self.role_map = role_map or {x: x for x in enum.Role}
        self.role_set_map = get_role_set_map(self.role_map)
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
        role_map: dict[Enum, Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.role_map = role_map or {x: x for x in enum.Role}
        self.role_set_map = get_role_set_map(self.role_map)
        self.props = kwargs


class BaseReadSelfResultsOnlyPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        role_map: dict[Enum, Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.role_map = role_map or {x: x for x in enum.Role}
        self.role_set_map = get_role_set_map(self.role_map)
        self.props = kwargs


class BaseReadUserPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        role_map: dict[Enum, Enum] | None = None,
        organization_admin_policy_crud_command_class: Type[
            CrudCommand
        ] = OrganizationAdminPolicyCrudCommand,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.role_map = role_map or {x: x for x in enum.Role}
        self.role_set_map = get_role_set_map(self.role_map)
        self.organization_admin_policy_crud_command_class = (
            organization_admin_policy_crud_command_class
        )
        self.props = kwargs


class BaseUpdateUserPolicy(Policy):
    def __init__(
        self,
        abac_service: BaseAbacService,
        role_map: dict[Enum, Enum] | None = None,
        **kwargs: Any,
    ):
        self.abac_service = abac_service
        self.role_map = role_map or {x: x for x in enum.Role}
        self.role_set_map = get_role_set_map(self.role_map)
        self.props = kwargs
