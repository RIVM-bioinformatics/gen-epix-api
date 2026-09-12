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


class AppComposer(CommonAppComposer):
    """Encapsulates casedb registrations for shared application composition.

    The composer binds the casedb domain, ordered service types, model and command
    substitutions, policy implementations, role generator, and RBAC service to
    the common composer. The common lifecycle creates configured repositories and
    services, registers roles and policies, and exposes dependencies consumed by
    the API layer; this class does not create FastAPI routers.

    Attributes:
        app: Composed command-handling application.
        services: Services indexed by their configured service type.
        repositories: Repositories indexed by their configured service type.
        registered_user_dependency: Dependency that resolves registered users.
        new_user_dependency: Dependency that resolves or creates new users.
        idp_user_dependency: Dependency that resolves identity-provider users.
    """

    def __init__(
        self,
        app_cfg: AppCfg,
        log_any: bool = True,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        """Initialize and run casedb application composition.

        Construction delegates immediately to the shared composition lifecycle.
        Depending on configuration, that lifecycle configures setup logging,
        initializes repositories and services, derives and registers roles and
        policies, and creates authentication dependencies.

        Args:
            app_cfg: Resolved casedb configuration used to compose dependencies.
            log_any: Whether any application logging is enabled.
            log_setup: Whether composition lifecycle events are logged.
            **kwargs: Additional options forwarded to shared composition.

        Raises:
            ValueError: If setup logging is enabled while all logging is disabled.
            InitializationServiceError: If configured values cannot be converted.
        """
        super().__init__(
            app_cfg,
            log_any=log_any,
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
