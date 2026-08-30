"""Compose SeqDB application dependencies from the configured environment."""

# pylint: disable=unused-import-alias
from typing import Any

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import AppComposer as CommonAppComposer
from gen_epix.seqdb.domain import DOMAIN, command, model
from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.policies import COMMON_POLICY_MAP
from gen_epix.seqdb.services import RbacService


class AppComposer(CommonAppComposer):
    def __init__(
        self,
        app_cfg: AppCfg,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        super().__init__(
            app_cfg,
            log_setup=log_setup,
            domain=DOMAIN,
            sorted_service_types=model.SORTED_SERVICE_TYPES,
            model_class_map=model.COMMON_MODEL_MAP,
            command_class_map=command.COMMON_COMMAND_MAP,
            policy_class_map=COMMON_POLICY_MAP,
            role_generator_class=RoleGenerator,
            rbac_service_class=RbacService,
            **kwargs,
        )
