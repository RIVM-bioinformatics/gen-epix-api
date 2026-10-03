"""Compose seqdb application dependencies from the configured environment."""

# pylint: disable=unused-import-alias
from typing import Any

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import AppComposer as CommonAppComposer
from gen_epix.commondb.env import NoAppComposer as CommonNoAppComposer
from gen_epix.seqdb.domain import DOMAIN, command, model
from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.policies import COMMON_POLICY_MAP
from gen_epix.seqdb.services import RbacService

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
    """Encapsulates shared infrastructure composition with seqdb dependencies."""

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
    """Encapsulates shared infrastructure composition for creating a seqdb app that
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
