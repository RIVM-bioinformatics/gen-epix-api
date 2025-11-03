from typing import Any

from gen_epix.casedb.domain import DOMAIN, command, model
from gen_epix.casedb.domain.policy import RoleGenerator
from gen_epix.casedb.policies import COMMON_POLICY_MAP
from gen_epix.casedb.services import RbacService
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import AppComposer as CommonAppComposer


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
            sorted_service_types=model.SORTED_SERVICE_TYPES,  # type: ignore[arg-type]
            model_class_map=model.COMMON_MODEL_MAP,  # type: ignore[arg-type]
            command_class_map=command.COMMON_COMMAND_MAP,  # type: ignore[arg-type]
            policy_class_map=COMMON_POLICY_MAP,
            role_generator_class=RoleGenerator,
            rbac_service_class=RbacService,
            **kwargs,
        )
