import traceback

# pylint: disable=unused-import-alias
from collections.abc import Iterable
from enum import Enum
from typing import Any, Callable, Type

from dynaconf import Dynaconf

from gen_epix import fastapp
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.base_env import BaseAppComposer
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import DOMAIN, command, enum, model
from gen_epix.commondb.domain.model import SORTED_SERVICE_TYPES
from gen_epix.commondb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.services import AuthService, RbacService
from gen_epix.commondb.services.abac import AbacService
from gen_epix.commondb.services.organization import OrganizationService
from gen_epix.commondb.services.system import SystemService
from gen_epix.commondb.services.user_manager import UserManager
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService


class App(fastapp.App):
    """
    Application class for the GenEpix FastAPI application. Overrides some properties
    to provide more specific types and linter support.
    """

    @property
    def cfg(self) -> Dynaconf:
        return super().cfg


class AppComposer(BaseAppComposer):
    def __init__(
        self,
        app_cfg: AppCfg,
        domain: Domain | None = None,
        sorted_service_types: tuple[Enum] | None = None,
        role_generator_class: Type[RoleGenerator] | None = None,
        rbac_service_class: Type[RbacService] | None = None,
        user_manager_class: Type[UserManager] | None = None,
        model_class_map: dict[Type[model.Model], Type[model.Model]] | None = None,
        command_class_map: (
            dict[Type[command.Command], Type[command.Command]] | None
        ) = None,
        policy_class_map: (
            dict[Type[fastapp.Policy], Type[fastapp.Policy]] | None
        ) = None,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        # Parse input
        self._app_cfg = app_cfg
        self._cfg = app_cfg.cfg
        self._domain = domain or DOMAIN
        self._sorted_service_types = sorted_service_types or SORTED_SERVICE_TYPES
        self._role_generator_class = role_generator_class or RoleGenerator
        self._rbac_service_class = rbac_service_class or RbacService
        self._user_manager_class = user_manager_class or UserManager
        self._model_class_map = model_class_map or {}
        self._command_class_map = command_class_map or {}
        self._policy_class_map = policy_class_map or {}
        self._log_setup = log_setup

        # Derive some properties
        self._role_map = self._role_generator_class.get_role_map()
        self._role_set_map = self._role_generator_class.get_role_set_map()
        self._role_permissions_map = (
            self._role_generator_class.get_role_permissions_map()
        )

        # Compose application
        data = self.compose_application(**kwargs)
        self._app: App = data["app"]
        self._services: dict[Enum, BaseService] = data["services"]
        self._repositories: dict[Enum, BaseRepository] = data["repositories"]
        self._registered_user_dependency: Callable = data["registered_user_dependency"]
        self._new_user_dependency: Callable = data["new_user_dependency"]
        self._idp_user_dependency: Callable = data["idp_user_dependency"]

    def compose_application(self) -> dict:

        # Get loggers
        cfg = self._app_cfg.cfg
        setup_logger = self._app_cfg.setup_logger
        app_logger = self._app_cfg.app_logger
        service_logger = self._app_cfg.service_logger

        # Compose application
        try:
            if self._log_setup:
                setup_logger.debug(
                    App.create_static_log_message(
                        "e8665136", "Starting composing application"
                    )
                )

                setup_logger.debug(
                    App.create_static_log_message(
                        "fb612692", "Initialising services and repositories"
                    )
                )

            # Initialize app
            app_impl = AppImplDetails(
                sorted_service_types=list(self._sorted_service_types),
                rbac_service_class=self._rbac_service_class,
                user_manager_class=self._user_manager_class,
                model_class_map=self._model_class_map,
                command_class_map=self._command_class_map,
                policy_class_map=self._policy_class_map,
                role_map=self._role_map,
                role_set_map=self._role_set_map,
                role_permissions_map=self._role_permissions_map,
            )
            app = App(
                name=self._app_cfg.app_name,
                domain=self._domain,
                cfg=self._app_cfg.cfg,
                impl=app_impl,
                logger=app_logger if self._log_setup else None,
                id_factory=cfg["service"]["defaults"]["props"]["id_factory"],
            )

            # Initialise repositories and services
            for service_type in self._sorted_service_types:
                service_cfg = cfg["service"][service_type.value]
                service_class = service_cfg["class"]
                service_props = service_cfg["props"]
                repository_cfg = cfg["repository"].get(service_type.value)

                # Create repository if necessary
                curr_repository = None
                if repository_cfg:
                    repository_class: Type[BaseRepository] = repository_cfg["class"]
                    repository_props = repository_cfg["props"]
                    if isinstance(repository_cfg["type"], str):
                        repository_type = enum.RepositoryType(repository_cfg["type"])
                    else:
                        repository_type = enum.RepositoryType(
                            repository_cfg["type"].value
                        )
                    entities = app.domain.get_dag_sorted_entities(
                        service_type=service_type
                    )
                    if self._log_setup:
                        setup_logger.debug(
                            app.create_log_message(
                                "db89f0a5",
                                f"Setting up {service_type.value} service with {repository_type.value} repository",
                            )
                        )
                    curr_repository = repository_class.create_repository(
                        entities=entities, **repository_props
                    )
                    # Add to overview of repositories
                    app_impl.repositories[service_type] = curr_repository

                # Create service, injecting app, repository, logger and props
                curr_service: BaseService = service_class(
                    app,
                    service_type=service_type,
                    repository=curr_repository,
                    logger=setup_logger if self._log_setup else None,
                    name=service_type.value,
                    **service_props,
                )
                if not self._log_setup:
                    curr_service.logger = service_logger
                # Add to overview of services
                app_impl.services[service_type] = curr_service

            # Get common services and types
            system_service_type = AppComposer._get_enum_from_list(
                self._sorted_service_types, "SYSTEM"
            )
            system_service = app_impl.services[system_service_type]
            assert isinstance(system_service, SystemService)
            auth_service_type = AppComposer._get_enum_from_list(
                self._sorted_service_types, "AUTH"
            )
            auth_service = app_impl.services[auth_service_type]
            assert isinstance(auth_service, AuthService)
            rbac_service_type = AppComposer._get_enum_from_list(
                self._sorted_service_types, "RBAC"
            )
            rbac_service = app_impl.services[rbac_service_type]
            assert isinstance(rbac_service, RbacService)
            abac_service_type = AppComposer._get_enum_from_list(
                self._sorted_service_types, "ABAC"
            )
            abac_service = app_impl.services[abac_service_type]
            assert isinstance(abac_service, AbacService)
            organization_service_type = AppComposer._get_enum_from_list(
                self._sorted_service_types, "ORGANIZATION"
            )
            organization_service = app_impl.services[organization_service_type]
            assert isinstance(organization_service, OrganizationService)

            # Set up roles
            rbac_service.register_roles(
                app_impl.role_permissions_map, app_impl.role_map[enum.Role.ROOT]
            )

            # Create and set user generator, which can create new users under different scenarios
            # such as from claims, from invitation, and when matching root secret
            app.user_manager = app_impl.user_manager_class(
                organization_service,
                rbac_service,
                root_cfg=app.cfg["service"]["auth"]["props"]["root"],
                automatic_new_user_cfg=app.cfg["service"]["auth"]["props"][
                    "automatic_new_user"
                ],  # set to None if no automatic new user
            )

            # Get current user and new user dependencies for injecting authentication in endpoints
            (
                app_impl.registered_user_dependency_or_none,
                app_impl.new_user_dependency_or_none,
                app_impl.idp_user_dependency_or_none,
            ) = auth_service.create_user_dependencies()

            # Register policies with app
            if self._log_setup:
                setup_logger.debug(
                    app.create_log_message("f329be4d", "Registering policies")
                )
            system_service.register_policies()
            rbac_service.register_policies()
            abac_service.register_policies()

            # Finalise process
            if self._log_setup:
                setup_logger.debug(
                    app.create_log_message("da172304", "Finished composing application")
                )

        except Exception as e:

            # Print error for deployment log, in regular log is not shown there
            traceback.print_exc()
            if self._log_setup:
                setup_logger.error(
                    App.create_static_log_message(
                        "db960800",
                        f"Error setting up application: {e}",
                    )
                )
            raise e

        return {
            "app": app,
            "services": app_impl.services,
            "repositories": app_impl.repositories,
            "registered_user_dependency": app_impl.registered_user_dependency,
            "new_user_dependency": app_impl.new_user_dependency,
            "idp_user_dependency": app_impl.idp_user_dependency,
        }

    @staticmethod
    def _get_enum_from_list(enums: Iterable[Enum], name: str) -> Enum:
        for enum_item in enums:
            if enum_item.name == name:
                return enum_item
        raise ValueError(f"Enum with name {name} not found")
