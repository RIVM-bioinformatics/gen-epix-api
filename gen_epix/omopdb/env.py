from typing import Any

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import AppEnv as CommonAppEnv
from gen_epix.omopdb.domain import DOMAIN, model
from gen_epix.omopdb.domain.model import SORTED_SERVICE_TYPES
from gen_epix.omopdb.domain.policy import RoleGenerator
from gen_epix.omopdb.services import RbacService, UserManager


class AppEnv(CommonAppEnv):
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
            sorted_service_types=SORTED_SERVICE_TYPES,  # type: ignore[arg-type]
            role_generator_class=RoleGenerator,
            rbac_service_class=RbacService,
            user_manager_class=UserManager,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            **kwargs,
        )
