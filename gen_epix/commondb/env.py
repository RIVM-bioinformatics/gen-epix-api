# pylint: disable=unused-import-alias
import copy
import traceback
from typing import Any, Callable, Type

from gen_epix.commondb.base_env import BaseAppEnv
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.repositories import (
    OrganizationDictRepository,
    OrganizationSARepository,
    SystemDictRepository,
    SystemSARepository,
    sa_model,
)
from gen_epix.commondb.repositories.abac_dict import AbacDictRepository
from gen_epix.commondb.repositories.abac_sa import AbacSARepository
from gen_epix.commondb.services import (
    AbacService,
    AuthService,
    OrganizationService,
    RbacService,
    SystemService,
)
from gen_epix.commondb.services.user_manager import UserManager
from gen_epix.fastapp.app import App
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService


class AppEnv(BaseAppEnv):
    SERVICE_DATA: dict[enum.ServiceType, dict[str, Any]] = {
        enum.ServiceType.ORGANIZATION: {
            "service_class": OrganizationService,
            "repository_class": {
                enum.RepositoryType.DICT: OrganizationDictRepository,
                enum.RepositoryType.SA_SQL: OrganizationSARepository,
            },
            "kwargs": {
                "user_class": model.User,
                "user_invitation_class": model.UserInvitation,
            },
            "repository_kwargs": {
                "user_class": model.User,
                "user_invitation_class": model.UserInvitation,
                "user_invitation_constraints_class": model.UserInvitationConstraints,
                "sa_user_class": sa_model.User,
                "sa_user_invitation_class": sa_model.UserInvitation,
            },
        },
        enum.ServiceType.AUTH: {
            "service_class": AuthService,
            "kwargs": {},
        },
        enum.ServiceType.RBAC: {
            "service_class": RbacService,
            "kwargs": {
                "role_enum": enum.Role,
            },
        },
        enum.ServiceType.SYSTEM: {
            "service_class": SystemService,
            "repository_class": {
                enum.RepositoryType.DICT: SystemDictRepository,
                enum.RepositoryType.SA_SQL: SystemSARepository,
            },
        },
        enum.ServiceType.ABAC: {
            "service_class": AbacService,
            "repository_class": {
                enum.RepositoryType.DICT: AbacDictRepository,
                enum.RepositoryType.SA_SQL: AbacSARepository,
            },
        },
    }
    for data in SERVICE_DATA.values():
        if "repository_class" not in data:
            continue
        if "repository_kwargs" not in data:
            data["repository_kwargs"] = {}
        data["repository_kwargs"][
            "service_metadata_fields"
        ] = sa_model.SERVICE_METADATA_FIELDS
        data["repository_kwargs"]["db_metadata_fields"] = sa_model.DB_METADATA_FIELDS
        data["repository_kwargs"][
            "generate_service_metadata"
        ] = sa_model.GENERATE_SERVICE_METADATA

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

        # Get logger for setup
        cfg = app_cfg.cfg
        setup_logger = app_cfg.setup_logger
        app_logger = app_cfg.app_logger
        service_logger = app_cfg.service_logger
        try:
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

            # Compose data to initialize repositories and services
            service_data = copy.deepcopy(AppEnv.SERVICE_DATA)
            for service_type in service_data:
                if "repository_class" in service_data[service_type]:
                    service_data[service_type]["repository_class"][
                        enum.RepositoryType.SA_SQLITE
                    ] = service_data[service_type]["repository_class"][
                        enum.RepositoryType.SA_SQL
                    ]

            # Initialise repositories and services
            services: dict[enum.ServiceType, BaseService] = {}
            repositories: dict[enum.ServiceType, BaseRepository] = {}
            for service_type in model.SORTED_SERVICE_TYPES:
                service_cfg = cfg["service"][service_type.value]
                data = service_data[service_type]
                service_props = service_cfg.props
                additional_service_kwargs: dict = data.get("kwargs", {})
                # Create repository if necessary
                if "repository_class" in data:
                    entities = app.domain.get_dag_sorted_entities(
                        service_type=service_type
                    )
                    repository_cfg = cfg["repository"][service_type.value]
                    repository_type = repository_cfg["type"]
                    if log_setup:
                        setup_logger.debug(
                            app.create_log_message(
                                "db89f0a5",
                                f"Setting up {service_type.value} service with {repository_type.value} repository",
                            )
                        )
                    repository_class = data["repository_class"][repository_type]
                    additional_repository_kwargs: dict = data.get(
                        "repository_kwargs", {}
                    )
                    curr_repository = AppEnv.create_repository(
                        service_type,
                        service_cfg.props.timestamp_factory,
                        entities,
                        repository_type,
                        repository_cfg,
                        repository_class,
                        **additional_repository_kwargs,
                    )
                else:
                    curr_repository = None
                # Create service, injecting app, repository, logger and props
                # service_class: Type[BaseService] = data["service_class"]
                service_class: Type[BaseService] = service_cfg["class"]
                curr_service: BaseService = service_class(
                    app,
                    service_type=service_type,
                    repository=curr_repository,
                    logger=setup_logger if log_setup else None,
                    name=service_type.value,
                    **service_props,
                    **additional_service_kwargs,
                )
                if not log_setup:
                    curr_service.logger = service_logger
                # Add to overview of services and repositories
                repositories[service_type] = curr_repository
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
