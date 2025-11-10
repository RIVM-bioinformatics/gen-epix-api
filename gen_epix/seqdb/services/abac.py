from __future__ import annotations

import logging
from typing import Any, Type

from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Command
from gen_epix.seqdb import policies
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.repository.abac import BaseAbacRepository
from gen_epix.seqdb.domain.service import BaseAbacService


class AbacService(BaseAbacService):
    CACHE_INVALIDATION_COMMANDS: tuple[Type[Command], ...] = tuple()

    def __init__(
        self,
        app: App,
        repository: BaseAbacRepository,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            app,
            repository=repository,
            organization_admin_policy_model_class=model.OrganizationAdminPolicy,
            user_crud_command_class=command.UserCrudCommand,
            is_organization_admin_policy_class=policies.IsOrganizationAdminPolicy,
            read_organization_results_only_policy_class=policies.ReadOrganizationResultsOnlyPolicy,
            read_self_results_only_policy_class=policies.ReadSelfResultsOnlyPolicy,
            read_user_policy_class=policies.ReadUserPolicy,
            update_user_policy_class=policies.UpdateUserPolicy,
            logger=logger,
            **kwargs,
        )
        self.repository: BaseAbacRepository
