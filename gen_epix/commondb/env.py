import datetime
import logging
import traceback

# pylint: disable=unused-import-alias
from collections.abc import Callable, Iterable
from enum import Enum
from typing import Any

from dynaconf import Dynaconf

from gen_epix import fastapp
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.base_env import BaseAppComposer
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import DOMAIN, enum, exc, model
from gen_epix.commondb.domain.model import SORTED_SERVICE_TYPES
from gen_epix.commondb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.repositories.dict_modifier import CommondbDictModelModifier
from gen_epix.commondb.repositories.sa_mapper import CommondbSAMapperFactory
from gen_epix.commondb.services import AuthService, RbacService
from gen_epix.commondb.services.abac import AbacService
from gen_epix.commondb.services.organization import OrganizationService
from gen_epix.commondb.services.system import SystemService
from gen_epix.commondb.services.user_manager import UserManager
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa import SARepository
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.util import create_ssl_context


class App(fastapp.App):
    """
    Application class for the GenEpix FastAPI application. Overrides some properties
    to provide more specific types and linter support.
    """

    @property
    def cfg(self) -> Dynaconf:
        return super().cfg


class AppComposer(BaseAppComposer):
    """
    Compose the commondb application by wiring services, repositories, and policies.
    """

    def __init__(
        self,
        app_cfg: AppCfg,
        domain: Domain | None = None,
        sorted_service_types: tuple[Enum, ...] | None = None,
        role_generator_class: type[RoleGenerator] | None = None,
        rbac_service_class: type[RbacService] | None = None,
        user_manager_class: type[UserManager] | None = None,
        model_class_map: dict[type[fastapp.Model], type[fastapp.Model]] | None = None,
        command_class_map: (
            dict[type[fastapp.Command], type[fastapp.Command]] | None
        ) = None,
        policy_class_map: (
            dict[type[fastapp.Policy], type[fastapp.Policy]] | None
        ) = None,
        log_setup: bool = True,
        **kwargs: Any,
    ):
        """Initialise the composer, parse configuration, and compose the application."""
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

        # Parse config to test presence of expected values and to convert any values as necessary, such as feature flags
        self._parse_config()

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

    def compose_application(self) -> dict[str, Any]:
        """
        Create the App instance, initialise all services and repositories, and register
        policies.
        """

        # Get loggers
        cfg = self._app_cfg.cfg
        setup_logger = self._app_cfg.setup_logger
        app_logger = self._app_cfg.app_logger
        service_logger = self._app_cfg.service_logger

        # Compose application
        try:
            if self._log_setup and setup_logger:
                self._setup_application_logging(setup_logger)

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
                feature_flags=cfg.get("feature_flags", {}),
            )
            ssl_context = create_ssl_context(
                host=cfg["app"]["host"], ssl_cert_file=cfg["app"].get("ssl_cert_file")
            )

            # Initialise services and where necessary repositories
            for service_type in self._sorted_service_types:
                self._init_service(
                    cfg,
                    setup_logger,
                    service_logger,
                    app_impl,
                    app,
                    ssl_context,
                    service_type,
                )

            # Get common services and types
            (
                system_service,
                auth_service,
                rbac_service,
                abac_service,
                organization_service,
            ) = self._get_services(app_impl)

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
                auto_created_user_cfg=app.cfg["service"]["auth"]["props"].get(
                    "auto_created_user"
                ),
            )

            # Get current user and new user dependencies for injecting authentication in endpoints
            (
                app_impl.registered_user_dependency_or_none,
                app_impl.new_user_dependency_or_none,
                app_impl.idp_user_dependency_or_none,
            ) = auth_service.create_user_dependencies()

            # Register policies with app
            if self._log_setup and setup_logger:
                setup_logger.debug(
                    app.create_log_message("f329be4d", "Registering policies")
                )
            system_service.register_policies()
            rbac_service.register_policies()
            abac_service.register_policies()

            # Finalise process
            if self._log_setup and setup_logger:
                setup_logger.debug(
                    app.create_log_message("da172304", "Finished composing application")
                )

        except Exception as e:

            # Print error for deployment log, in regular log is not shown there
            traceback.print_exc()
            if self._log_setup and setup_logger:
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

    def _get_services(
        self, app_impl: AppImplDetails
    ) -> tuple[
        SystemService, AuthService, RbacService, AbacService, OrganizationService
    ]:
        """Retrieve the core services from the application implementation details."""
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
        return (
            system_service,
            auth_service,
            rbac_service,
            abac_service,
            organization_service,
        )

    def _init_service(
        self,
        cfg: Dynaconf,
        setup_logger: logging.Logger,
        service_logger: logging.Logger,
        app_impl: AppImplDetails,
        app: App,
        ssl_context: Any,
        service_type: Enum,
    ) -> None:
        """Initialise a single service and its repository from configuration."""
        service_cfg = cfg["service"][service_type.value]
        service_class = service_cfg["class"]
        service_props = service_cfg["props"]
        repository_cfg = cfg["repository"].get(service_type.value)

        # Create repository if necessary
        curr_repository = None
        if repository_cfg:
            repository_class: type[BaseRepository] = repository_cfg["class"]
            repository_props = repository_cfg["props"]
            if isinstance(repository_cfg["type"], str):
                repository_type = enum.RepositoryType(repository_cfg["type"])
            else:
                repository_type = enum.RepositoryType(repository_cfg["type"].value)
            entities = app.domain.get_dag_sorted_entities(service_type=service_type)
            if self._log_setup and setup_logger:
                setup_logger.debug(
                    app.create_log_message(
                        "db89f0a5",
                        f"Setting up {service_type.value} service with {repository_type.value} repository",
                    )
                )
            # Inject a CommondbSAMapperFactory for SA-backed repositories so that
            # mapper update logic (created_at/modified_at protection, modified_by
            # stamping) lives in the db layer rather than in fastapp.
            factory_kwargs: dict[str, Any] = {}
            if issubclass(repository_class, SARepository):
                factory_kwargs["sa_mapper_factory"] = CommondbSAMapperFactory()
            # Create repository
            curr_repository = repository_class.create_repository(
                entities=entities, **factory_kwargs, **repository_props
            )
            # Register a CommondbDictModelModifier for every model class that carries
            # RowMetadataMixin fields, mirroring what CommondbSAMapper does for SA.
            if isinstance(curr_repository, DictRepository):
                modifier = CommondbDictModelModifier()
                for entity in entities:
                    if not entity.persistable:
                        continue
                    if not issubclass(entity.model_class, model.ModelNoId):
                        continue
                    curr_repository.register_model_modifier(
                        entity.model_class, modifier
                    )
                # TODO: Check if this is correct or the data should be updated...
                # Backfill timestamps on objects loaded from demo pickle files.
                # Pkl demo data was serialized before the modifier existed, so
                # created_at / modified_at are None on all pre-loaded objects.
                # This runs for every DICT-backed service (omopdb, casedb,
                # seqdb, commondb) so all repositories are treated consistently.
                _DEFAULT_TIMESTAMP = datetime.datetime(
                    2000, 1, 1, tzinfo=datetime.timezone.utc
                )
                for entity in entities:
                    if not entity.persistable:
                        continue
                    if not issubclass(entity.model_class, model.ModelNoId):
                        continue
                    for stored_obj in curr_repository.db.get(
                        entity.model_class, {}
                    ).values():
                        assert isinstance(stored_obj, model.ModelNoId)
                        if stored_obj.modified_at is None:
                            stored_obj.modified_at = _DEFAULT_TIMESTAMP
                        if stored_obj.created_at is None:
                            stored_obj.created_at = _DEFAULT_TIMESTAMP
            # Add to overview of repositories
            app_impl.repositories[service_type] = curr_repository

            # Create service, injecting app, repository, logger and props
        curr_service: BaseService = service_class(
            app,
            service_type=service_type,
            repository=curr_repository,
            logger=service_logger,
            setup_logger=setup_logger if self._log_setup else None,
            name=service_type.value,
            ssl_context=ssl_context,
            **service_props,
        )
        # Add to overview of services
        app_impl.services[service_type] = curr_service

    def _setup_application_logging(self, setup_logger: logging.Logger) -> None:
        """Log the start of the application composition process."""
        setup_logger.debug(
            App.create_static_log_message("e8665136", "Starting composing application")
        )
        setup_logger.debug(
            App.create_static_log_message(
                "fb612692", "Initialising services and repositories"
            )
        )

    def _parse_config(self) -> None:
        """
        Parse configuration values to test presence of expected values and convert any
        values as necessary, such as feature flags.
        """
        # TODO: expand with a framework for parsing and validating config values, potentially using Pydantic classes to define expected config structure and types, and to perform parsing and validation.
        cfg_content_types = [
            ("feature_flags", None, bool),  # All feature flags
            ("service", "auth", "props", "auto_create_new_users", bool),
            ("service", "auth", "props", "root_token_time_to_live", int),
        ]
        cfg = self._app_cfg.cfg
        # Convert boolean values
        for cfg_path in cfg_content_types:
            # Traverse config path to get value
            cfg_section = cfg
            path_exists = True
            for ancestor_key in cfg_path[:-2]:
                if ancestor_key not in cfg_section:
                    path_exists = False
                    break
                cfg_section = cfg_section[ancestor_key]
            if not path_exists:
                # Config path does not exist
                continue
            # Check if value is of the correct type, and if not attempt to convert
            if cfg_path[-2] is None:
                # Special case: all leaf keys should have this content type
                leaf_dict = cfg_section
            else:
                # Single leaf key with content type
                leaf_dict = {cfg_path[-2]: cfg_section[cfg_path[-2]]}
            for leaf_key, leaf_value in leaf_dict.items():
                is_valid, converted_value = AppComposer._verify_type(
                    leaf_value, cfg_path[-1]
                )
                if not is_valid:
                    raise exc.InitializationServiceError(
                        f"Invalid value for config {'.'.join((str(x) for x in cfg_path + (leaf_key,)))}: expected type {cfg_path[-1].__name__}"
                    )
                if converted_value != leaf_value:
                    cfg_section[leaf_key] = converted_value

    def _verify_type(value: Any, content_type: type) -> Any:
        """Verify and optionally convert a value to the expected type."""
        if isinstance(value, content_type):
            return True, value
        if value is None:
            # Skip None as the value may be optional
            return True, value
        if content_type is bool:
            is_bool, converted_value = AppComposer.convert_to_bool(value)
            return is_bool, converted_value
        elif content_type is int:
            converted_value = int(value)
            return True, converted_value
        raise exc.InitializationServiceError(
            f"Unsupported content type {content_type} for config parsing"
        )

    @staticmethod
    def _get_enum_from_list(enums: Iterable[Enum], name: str) -> Enum:
        """Return the enum member with the given name from an iterable of enums."""
        for enum_item in enums:
            if enum_item.name == name:
                return enum_item
        raise ValueError(f"Enum with name {name} not found")

    @staticmethod
    def convert_to_bool(value: Any) -> tuple[bool, bool]:
        """
        Convert a value to boolean if possible. Returns a tuple of (success,
        converted_value).
        Accepts boolean values and strings "true", "1", "false", "0" (case
        insensitive). If conversion is not possible, returns (False, False).
        """
        if isinstance(value, bool):
            return True, value
        if isinstance(value, str):
            if value.lower() in {"true", "1"}:
                return True, True
            elif value.lower() in {"false", "0"}:
                return True, False
        return False, False
