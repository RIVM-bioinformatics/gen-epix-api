# pylint: disable=unused-import-alias
import copy
import traceback
from typing import Any, Callable, Type

from gen_epix.common.config import AppCfg
from gen_epix.common.env import BaseAppEnv
from gen_epix.fastapp import App, BaseService
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.domain.policy import RoleGenerator
from gen_epix.seqdb.domain.service import ORDERED_SERVICE_TYPES
from gen_epix.seqdb.repositories import (
    OrganizationDictRepository,
    OrganizationSARepository,
    SeqDictRepository,
    SeqSARepository,
    SystemDictRepository,
    SystemSARepository,
    sa_model,
)
from gen_epix.seqdb.services import (
    AbacService,
    AuthService,
    OrganizationService,
    RbacService,
    SeqService,
    SystemService,
    UserManager,
)


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
        enum.ServiceType.SEQ: {
            "service_class": SeqService,
            "repository_class": {
                enum.RepositoryType.DICT: SeqDictRepository,
                enum.RepositoryType.SA_SQL: SeqSARepository,
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
        },
    }

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
                id_factory=cfg.service.defaults.id_factory,
            )

            # Compose data to initialize repositories and services
            service_data = copy.deepcopy(AppEnv.SERVICE_DATA)
            service_data[enum.ServiceType.AUTH].update(
                {
                    "kwargs": {
                        "idps_cfg": cfg.IDPS_CONFIG,
                    },
                }
            )
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
            for service_type in ORDERED_SERVICE_TYPES:
                data = service_data[service_type]
                props = {
                    x: y
                    for x, y in cfg.service[service_type.value.lower()].items()
                    if x not in {"id_factory", "timestamp_factory"}
                }
                id_factory = cfg.service[service_type.value.lower()]["id_factory"]
                timestamp_factory = cfg.service[service_type.value.lower()][
                    "timestamp_factory"
                ]
                additional_service_kwargs: dict = data.get("kwargs", {})  # type: ignore

                # Create repository if necessary
                if "repository_class" in data:
                    entities = app.domain.get_dag_sorted_entities(
                        service_type=service_type
                    )
                    repository_type = cfg.secret["db"]["repository_type"]
                    repository_cfg = cfg.secret["repository"][
                        repository_type.value.lower()
                    ][service_type.value.lower()]
                    if log_setup:
                        setup_logger.debug(
                            app.create_log_message(
                                "db89f0a5",
                                f"Setting up {service_type.value} service with {repository_type.value} repository",
                            )
                        )
                    repository_class = data["repository_class"][repository_type]
                    additional_repository_kwargs: dict = data.get("repository_kwargs", {})  # type: ignore
                    curr_repository = AppEnv.create_repository(
                        service_type,
                        timestamp_factory,
                        entities,
                        repository_type,
                        repository_cfg,
                        repository_class,
                        **additional_repository_kwargs,
                    )
                else:
                    curr_repository = None
                # Create service, injecting app, repository, logger and props
                service_class: Type[BaseService] = data["service_class"]
                curr_service: BaseService = service_class(
                    app,
                    service_type=service_type,
                    repository=curr_repository,
                    logger=setup_logger if log_setup else None,
                    props=props,
                    name=service_type.value,
                    id_factory=id_factory,
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
            service.register_roles(RoleGenerator.ROLE_PERMISSIONS)

            # Create and set user generator, which can create new users under different scenarios
            # such as from claims, from invitation, and when matching root secret
            app.user_manager = UserManager(
                model.User,
                model.UserInvitation,
                services[enum.ServiceType.ORGANIZATION],  # type: ignore
                services[enum.ServiceType.RBAC],  # type: ignore
                cfg.secret.root,
                automatic_new_user_cfg=cfg.secret.automatic_new_user,  # set to None if no automatic new user
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
            services[enum.ServiceType.RBAC].register_policies()  # type: ignore
            services[enum.ServiceType.ABAC].register_policies()  # type: ignore
            services[enum.ServiceType.SYSTEM].register_policies()  # type: ignore

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
