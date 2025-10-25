import traceback

# pylint: disable=unused-import-alias
from collections.abc import Iterable
from enum import Enum
from typing import Any, Callable, Type

from gen_epix import fastapp
from gen_epix.commondb.base_env import BaseAppEnv
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import DOMAIN, enum, model
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
    """CommonDB application class."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.services: dict[Enum, fastapp.BaseService] = {}
        self.repositories: dict[Enum, fastapp.BaseRepository] = {}
        self.registered_user_dependency: model.User | None = None
        self.new_user_dependency: model.User | None = None
        self.idp_user_dependency: model.User | None = None


class AppEnv(BaseAppEnv):
    def __init__(
        self,
        app_cfg: AppCfg,
        domain: Domain | None = None,
        sorted_service_types: tuple[Enum] | None = None,
        role_generator_class: Type[RoleGenerator] | None = None,
        rbac_service_class: Type[RbacService] | None = None,
        user_manager_class: Type[UserManager] | None = None,
        user_class: Type[model.User] | None = None,
        user_invitation_class: Type[model.UserInvitation] | None = None,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        self._app_cfg = app_cfg
        self._cfg = app_cfg.cfg
        self._domain = domain or DOMAIN
        self._sorted_service_types = sorted_service_types or SORTED_SERVICE_TYPES
        self._role_generator_class = role_generator_class or RoleGenerator
        self._rbac_service_class = rbac_service_class or RbacService
        self._user_manager_class = user_manager_class or UserManager
        self._user_class = user_class or model.User
        self._user_invitation_class = user_invitation_class or model.UserInvitation
        self._log_setup = log_setup

        # Compose application
        data = self.compose_application(app_cfg, **kwargs)
        self._app: App = data["app"]
        self._services: dict[Enum, BaseService] = data["services"]
        self._repositories: dict[Enum, BaseRepository] = data["repositories"]
        self._registered_user_dependency: Callable = data["registered_user_dependency"]
        self._new_user_dependency: Callable = data["new_user_dependency"]
        self._idp_user_dependency: Callable = data["idp_user_dependency"]

    def compose_application(self, app_cfg: AppCfg, **kwargs: Any) -> dict:

        # Get loggers
        cfg = app_cfg.cfg
        setup_logger = app_cfg.setup_logger
        app_logger = app_cfg.app_logger
        service_logger = app_cfg.service_logger

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
            app = App(
                name="main",
                domain=kwargs.get("domain", self._domain),
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
                    app.repositories[service_type] = curr_repository

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
                app.services[service_type] = curr_service

            # Get common services and types
            system_service_type = AppEnv._get_enum_from_list(
                self._sorted_service_types, "SYSTEM"
            )
            system_service = app.services[system_service_type]
            assert isinstance(system_service, SystemService)
            auth_service_type = AppEnv._get_enum_from_list(
                self._sorted_service_types, "AUTH"
            )
            auth_service = app.services[auth_service_type]
            assert isinstance(auth_service, AuthService)
            rbac_service_type = AppEnv._get_enum_from_list(
                self._sorted_service_types, "RBAC"
            )
            rbac_service = app.services[rbac_service_type]
            assert isinstance(rbac_service, RbacService)
            abac_service_type = AppEnv._get_enum_from_list(
                self._sorted_service_types, "ABAC"
            )
            abac_service = app.services[abac_service_type]
            assert isinstance(abac_service, AbacService)
            organization_service_type = AppEnv._get_enum_from_list(
                self._sorted_service_types, "ORGANIZATION"
            )
            organization_service = app.services[organization_service_type]
            assert isinstance(organization_service, OrganizationService)

            # Set up roles
            root_role = AppEnv._get_enum_from_list(self._role_generator_class.ROLE_PERMISSIONS, "ROOT")  # type: ignore[arg-type]
            rbac_service.register_roles(
                self._role_generator_class.ROLE_PERMISSIONS, root_role=root_role  # type: ignore[arg-type]
            )

            # Create and set user generator, which can create new users under different scenarios
            # such as from claims, from invitation, and when matching root secret
            app.user_manager = self._user_manager_class(
                self._user_class,
                self._user_invitation_class,
                organization_service,
                rbac_service,
                cfg["service"]["auth"]["props"]["root"],
                automatic_new_user_cfg=cfg["service"]["auth"]["props"][
                    "automatic_new_user"
                ],  # set to None if no automatic new user
            )

            # Get current user and new user dependencies for injecting authentication in endpoints
            (
                app.registered_user_dependency,
                app.new_user_dependency,
                app.idp_user_dependency,
            ) = auth_service.create_user_dependencies()

            # Register security policies with app
            if self._log_setup:
                setup_logger.debug(
                    app.create_log_message("f329be4d", "Registering security policies")
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
            "services": app.services,
            "repositories": app.repositories,
            "registered_user_dependency": app.registered_user_dependency,
            "new_user_dependency": app.new_user_dependency,
            "idp_user_dependency": app.idp_user_dependency,
        }

    # TODO: make base class method abstract and implement here with new repository_class.create_repository method
    # @classmethod
    # def create_repository(
    #     cls,
    #     service_type: Enum,
    #     timestamp_factory: Callable,
    #     entities: list[Entity],
    #     repository_type: Enum,
    #     repository_cfg: dict[str, Any],
    #     repository_class: Type[BaseRepository],
    #     **kwargs: Any,
    # ) -> BaseRepository:
    #     repository: BaseRepository
    #     repository = repository_class.create_repository(
    #         entities=entities,
    #         timestamp_factory=timestamp_factory,
    #         **repository_cfg["props"],
    #         **kwargs,
    #     )
    #     return repository

    @staticmethod
    def _get_enum_from_list(enums: Iterable[Enum], name: str) -> Enum:
        for enum_item in enums:
            if enum_item.name == name:
                return enum_item
        raise ValueError(f"Enum with name {name} not found")
