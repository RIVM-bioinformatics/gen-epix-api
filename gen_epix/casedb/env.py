"""Compose casedb application dependencies from the configured environment.

``AppComposer`` supplies casedb domain metadata and implementations to the shared
commondb composition lifecycle. The shared composer owns configuration parsing,
repository and service creation, role and policy registration, and authentication
dependency setup; FastAPI and router composition remain in ``casedb.app``.
"""

from typing import Any

from gen_epix.casedb.domain import DOMAIN, command, model
from gen_epix.casedb.domain.policy import RoleGenerator
from gen_epix.casedb.policies import COMMON_POLICY_MAP
from gen_epix.casedb.services import RbacService
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import AppComposer as CommonAppComposer
from gen_epix.commondb.env import NoAppComposer as CommonNoAppComposer

_KWARGS = {
    "domain": DOMAIN,
    "sorted_service_types": model.SORTED_SERVICE_TYPES,
    "model_class_map": model.COMMON_MODEL_MAP,
    "command_class_map": command.COMMON_COMMAND_MAP,
    "policy_class_map": COMMON_POLICY_MAP,
    "role_generator_class": RoleGenerator,
    "rbac_service_class": RbacService,
}


class AppComposer(CommonAppComposer):
    """Encapsulates shared infrastructure composition with casedb dependencies."""

    def __init__(
        self,
        app_cfg: AppCfg,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        """Initialize composer with models, commands, policies, and roles.

        Args:
            app_cfg: Application configuration used to compose dependencies.
            log_setup: Whether to configure application logging.
            **kwargs: Additional commondb composer configuration.
        """
        super().__init__(
            app_cfg,
            log_setup=log_setup,
            **_KWARGS,  # type: ignore[arg-type]
            **kwargs,
        )


class NoAppComposer(CommonNoAppComposer):
    """Encapsulates shared infrastructure composition for creating a casedb app that
    raises an exception on all commands."""

    def __init__(
        self,
        app_cfg: AppCfg,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        """Initialize composition.

        Args:
            app_cfg: Application configuration used to compose dependencies.
            log_setup: Whether to configure application logging.
            **kwargs: Additional commondb composer configuration.
        """
        super().__init__(
            app_cfg,
            log_setup=log_setup,
            **_KWARGS,  # type: ignore[arg-type]
            **kwargs,
        )
