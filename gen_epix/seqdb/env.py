# pylint: disable=unused-import-alias
import traceback
from typing import Any, Callable, Type

import httpx

from gen_epix.commondb.base_env import BaseAppEnv
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.env import BaseAppEnv
from gen_epix.fastapp import App, BaseService
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.domain.model import SORTED_SERVICE_TYPES
from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.services import RbacService, UserManager


class AppEnv(BaseAppEnv):
    def __init__(self, app_cfg: AppCfg, log_setup: bool = True, **kwargs: Any):
        self._cfg = app_cfg.cfg
        data = self.compose_application(app_cfg, log_setup=log_setup, **kwargs)
        self._app: App = data["app"]
        self._services: dict[enum.ServiceType, BaseService] = data["services"]
        self._repositories: dict[enum.RepositoryType, BaseRepository] = data[
            "repositories"
        ]
        self._registered_user_dependency: Callable = data["registered_user_dependency"]
        self._new_user_dependency: Callable = data["new_user_dependency"]
        self._idp_user_dependency: Callable = data["idp_user_dependency"]

    @staticmethod
    def compose_application(
        app_cfg: AppCfg, log_setup: bool = True, **kwargs: Any
    ) -> dict:

        try:
            # Get logger for setup
            cfg = app_cfg.cfg
            setup_logger = app_cfg.setup_logger
            app_logger = app_cfg.app_logger
            service_logger = app_cfg.service_logger
            if log_setup:
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
                domain=kwargs.get("domain", DOMAIN),
                logger=app_logger if log_setup else None,
                id_factory=cfg["service"]["defaults"]["props"]["id_factory"],
            )

            # Initialise repositories and services
            services: dict[enum.ServiceType, BaseService] = {}
            repositories: dict[enum.ServiceType, BaseRepository] = {}
            for service_type in SORTED_SERVICE_TYPES:
                service_cfg = cfg["service"][service_type.value]
                service_class = service_cfg["class"]
                service_props = service_cfg["props"]
                repository_cfg = cfg["repository"].get(service_type.value)

                # Create repository if necessary
                curr_repository = None
                if repository_cfg:
                    repository_class: Type[BaseRepository] = repository_cfg["class"]
                    repository_props = repository_cfg["props"]
                    repository_type = enum.RepositoryType(repository_cfg["type"])
                    entities = app.domain.get_dag_sorted_entities(
                        service_type=service_type
                    )
                    if log_setup:
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
                    repositories[service_type] = curr_repository
                # Create service, injecting app, repository, logger and props
                curr_service: BaseService = service_class(
                    app,
                    service_type=service_type,
                    repository=curr_repository,
                    logger=setup_logger if log_setup else None,
                    name=service_type.value,
                    **service_props,
                )
                if not log_setup:
                    curr_service.logger = service_logger
                # Add to overview of services
                services[service_type] = curr_service

            # Set up roles
            service = services[enum.ServiceType.RBAC]
            assert isinstance(service, RbacService)
            service.register_roles(
                RoleGenerator.ROLE_PERMISSIONS, root_role=enum.Role.ROOT
            )

            # Create and set user generator, which can create new users under different scenarios
            # such as from claims, from invitation, and when matching root secret
            app.user_manager = UserManager(
                model.User,
                model.UserInvitation,
                services[enum.ServiceType.ORGANIZATION],  # type: ignore
                services[enum.ServiceType.RBAC],  # type: ignore
                cfg["service"]["auth"]["props"]["root"],
                automatic_new_user_cfg=cfg["service"]["auth"]["props"][
                    "automatic_new_user"
                ],  # set to None if no automatic new user
            )

            # Get current user and new user dependencies for injecting authentication in endpoints
            registered_user_dependency, new_user_dependency, idp_user_dependency = services[  # type: ignore
                enum.ServiceType.AUTH
            ].create_user_dependencies()

            # Register security policies with app
            if log_setup:
                setup_logger.debug(
                    app.create_log_message("f329be4d", "Registering security policies")
                )
            services[enum.ServiceType.SYSTEM].register_policies()  # type: ignore
            services[enum.ServiceType.RBAC].register_policies()  # type: ignore
            services[enum.ServiceType.ABAC].register_policies()  # type: ignore

            # Finalise process
            if log_setup:
                setup_logger.debug(
                    app.create_log_message("da172304", "Finished composing application")
                )

        except Exception as e:

            # Print error for deployment log, in regular log is not shown there
            traceback.print_exc()
            if log_setup:
                setup_logger.error(
                    App.create_static_log_message(
                        "db960800",
                        f"Error setting up application: {e}",
                    )
                )
            raise e

        return {
            "app": app,
            "services": services,
            "repositories": repositories,
            "registered_user_dependency": registered_user_dependency,
            "new_user_dependency": new_user_dependency,
            "idp_user_dependency": idp_user_dependency,
        }


def get_jwt(client_id: str, client_secret: str) -> str:
    TOKEN_URL = "https://pre-login.rivm.nl/broker/sp/oidc/token"
    SCOPE = "openid profile email"

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": SCOPE,
    }

    with httpx.Client() as client:
        response = client.post(
            TOKEN_URL,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token_response = response.json()

    return token_response["access_token"]
