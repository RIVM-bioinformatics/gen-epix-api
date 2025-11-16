import abc
from collections.abc import Callable
from typing import Any
from uuid import UUID

from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp.model import Policy


class BaseAbacPolicy(Policy):
    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        super().__init__()
        self.abac_service = abac_service
        self.props = kwargs


class BaseIsOrganizationAdminPolicy(BaseAbacPolicy):

    @abc.abstractmethod
    def register_retrieve_organization_ids_handler(
        self,
        command_class: type[Command],
        handler: Callable[[Command], set[UUID]],
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_organization_ids(self, cmd: Command) -> set[UUID]:
        raise NotImplementedError


class BaseReadOrganizationResultsOnlyPolicy(BaseAbacPolicy):
    pass


class BaseReadSelfResultsOnlyPolicy(BaseAbacPolicy):
    pass


class BaseReadUserPolicy(BaseAbacPolicy):
    pass


class BaseUpdateUserPolicy(BaseAbacPolicy):
    pass
