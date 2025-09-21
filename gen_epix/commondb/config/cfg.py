"""Refactored configuration management using Strategy Pattern."""

import abc
import json
import logging
import logging.config as logging_config
import os
from enum import Enum
from locale import getpreferredencoding
from pathlib import Path
from typing import Any, Type
from urllib.parse import quote_plus

import yaml  # type: ignore[import-untyped]
from sqlalchemy import URL

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.factory import IdFactory, TimestampFactory
from gen_epix.commondb.config.secret_provider import (
    SecretLoadError,
    SecretProviderFactory,
)
from gen_epix.commondb.config.settings import SettingsManager
from gen_epix.fastapp import App


class BaseAppCfg(abc.ABC):
    """Abstract base class for application configuration."""

    def __init__(self) -> None:
        self._app_name: str
        self._service_type_enum: Type[Enum]
        self._repository_type_enum: Type[Enum]
        self._log_setup: bool
        self._settings: DictProxy
        self._secrets: DictProxy
        self._setup_logger: logging.Logger
        self._api_logger: logging.Logger
        self._app_logger: logging.Logger
        self._service_logger: logging.Logger

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    def service_type_enum(self) -> Type[Enum]:
        return self._service_type_enum

    @property
    def repository_type_enum(self) -> Type[Enum]:
        return self._repository_type_enum

    @property
    def log_setup(self) -> bool:
        return self._log_setup

    @property
    def settings(self) -> DictProxy:
        return self._settings

    @property
    def secrets(self) -> DictProxy:
        return self._secrets

    @property
    def setup_logger(self) -> logging.Logger:
        return self._setup_logger

    @property
    def api_logger(self) -> logging.Logger:
        return self._api_logger

    @property
    def app_logger(self) -> logging.Logger:
        return self._app_logger

    @property
    def service_logger(self) -> logging.Logger:
        return self._service_logger

    # Backward compatibility - cfg property that combines settings and secrets
    @property
    def cfg(self) -> Any:
        """Backward compatibility property that provides dynaconf-like access."""
        return ConfigProxy(self._settings, self._secrets)


class ConfigProxy:
    """Proxy class to provide backward compatibility with old cfg access pattern."""

    def __init__(self, settings: DictProxy, secrets: DictProxy):
        self._settings = settings
        self._secrets = secrets
        # Create a secret proxy for backward compatibility
        self.secret = secrets

    def __getattr__(self, name: str) -> Any:
        # First try to get from settings
        if hasattr(self._settings, name):
            return getattr(self._settings, name)

        # Then try from secrets
        if name in self._secrets:
            return (
                DictProxy(data=self._secrets[name])
                if isinstance(self._secrets[name], dict)
                else self._secrets[name]
            )

        raise AttributeError(f"'ConfigProxy' object has no attribute '{name}'")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default


class AppCfg(BaseAppCfg):
    """Main application configuration class using Strategy Pattern."""

    @staticmethod
    def _prefix_envvar(
        envvar_prefix: str | None, envvar: str, delimiter: str = "_"
    ) -> str:
        """Create prefixed environment variable name."""
        if envvar_prefix:
            return f"{envvar_prefix}{delimiter}{envvar}"
        return envvar

    @staticmethod
    def _prefix_logger(
        logger_prefix: str | None, logger_name: str, delimiter: str = "."
    ) -> str:
        """Create prefixed logger name."""
        if logger_prefix:
            return f"{logger_prefix}{delimiter}{logger_name}"
        return logger_name

    def __init__(
        self,
        app_name: str,
        service_type_enum: Type[Enum],
        repository_type_enum: Type[Enum],
        log_setup: bool = True,
        logger_prefix: str | None = None,
        envvar_prefix: str | None = None,
        logging_config_file_envvar: str = "LOGGING_CONFIG_FILE",
        idps_config_file_envvar: str = "IDPS_CONFIG_FILE",
        logging_level_from_secret_envvar: str = "LOGGING_LEVEL_FROM_SECRET",
        # Legacy parameters for backward compatibility - now ignored
        settings_dir_envvar: str = "SETTINGS_DIR",
        secrets_dir_envvar: str | None = "SECRETS_DIR",
        settings_files: list[str] | None = None,
        cfg_key_map: dict[str, str] | None = None,
    ):
        """Initialize application configuration.

        Args:
            app_name: Name of the application (e.g., 'commondb', 'casedb')
            service_type_enum: Enum of service types
            repository_type_enum: Enum of repository types
            log_setup: Whether to set up logging
            logger_prefix: Prefix for logger names (defaults to app_name.lower())
            envvar_prefix: Prefix for environment variables (defaults to app_name.upper())
            logging_config_file_envvar: Environment variable for logging config file
            idps_config_file_envvar: Environment variable for identity provider config
            logging_level_from_secret_envvar: Environment variable to control log level from secrets
        """
        # Parse input
        logger_prefix = logger_prefix or app_name.lower()
        envvar_prefix = envvar_prefix or f"{app_name.upper()}_"

        # Add some properties
        self._app_name = app_name
        self._service_type_enum = service_type_enum
        self._repository_type_enum = repository_type_enum
        self._log_setup = log_setup

        # Configure and set loggers
        self._init_configure_loggers(
            envvar_prefix, logging_config_file_envvar, logger_prefix
        )

        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "c6010f14", "Starting setting up config data with new architecture"
                )
            )

        # Load settings using new SettingsManager
        self._init_load_settings(envvar_prefix, log_setup)

        # Load secrets using new SecretProviderFactory
        self._init_load_secrets(envvar_prefix, log_setup)

        # Set timestamp and ID factory per service
        self._init_set_factories_for_services()

        # Set log level from secrets
        self._init_set_log_level(
            envvar_prefix, logging_level_from_secret_envvar, log_setup
        )

        # Add authentication settings
        self._init_add_authentication_cfg(idps_config_file_envvar)

        # Fill in repository connection string parameters per service
        self._init_repository_cfg()

        # Finalise process
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "cdb7abcb", "Finished setting up config data with new architecture"
                )
            )

    def _init_configure_loggers(
        self,
        envvar_prefix: str | None,
        logging_config_file_envvar: str,
        logger_prefix: str | None,
    ) -> None:
        """Configure loggers from logging configuration file."""
        logging_config_file = os.environ[f"{envvar_prefix}{logging_config_file_envvar}"]
        with open(logging_config_file, "rt", encoding=getpreferredencoding()) as handle:
            logging_config_yaml = yaml.safe_load(handle.read())
            logging_config.dictConfig(logging_config_yaml)

        # Get loggers and put as attributes
        self._setup_logger = logging.getLogger(
            AppCfg._prefix_logger(logger_prefix, "setup")
        )
        self._api_logger = logging.getLogger(
            AppCfg._prefix_logger(logger_prefix, "api")
        )
        self._app_logger = logging.getLogger(
            AppCfg._prefix_logger(logger_prefix, "app")
        )
        self._service_logger = logging.getLogger(
            AppCfg._prefix_logger(logger_prefix, "service")
        )
        self._logging_config_yaml = logging_config_yaml

    def _init_load_settings(self, envvar_prefix: str, log_setup: bool) -> None:
        """Load settings using SettingsManager."""
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "d5fd558a", "Loading settings with SettingsManager"
                )
            )

        settings_manager = SettingsManager(prefix=envvar_prefix)
        self._settings = settings_manager.load_settings()

        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "a7b3c4d5", f"Loaded settings from {type(self._settings).__name__}"
                )
            )

    def _init_load_secrets(self, envvar_prefix: str, log_setup: bool) -> None:
        """Load secrets using SecretProviderFactory."""
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "c61368d6", "Loading secrets with SecretProviderFactory"
                )
            )

        try:
            self._secrets = SecretProviderFactory.load_secrets(prefix=envvar_prefix)

            if log_setup:
                strategy_env_var = f"{envvar_prefix}_SECRETS_STRATEGY"
                strategy = os.environ.get(strategy_env_var, "unknown")
                self.setup_logger.debug(
                    App.create_static_log_message(
                        "f8e7d6c5", f"Loaded secrets using strategy: {strategy}"
                    )
                )

        except SecretLoadError as e:
            if log_setup:
                self.setup_logger.error(
                    App.create_static_log_message(
                        "e1f2a3b4", f"Failed to load secrets: {e}"
                    )
                )
            raise

    def _init_set_log_level(
        self,
        envvar_prefix: str | None,
        logging_level_from_secret_envvar: str,
        log_setup: bool,
    ) -> None:
        """Set log level from secrets if configured to do so."""
        logging_config_yaml = self._logging_config_yaml

        if bool(
            int(
                os.environ.get(
                    AppCfg._prefix_envvar(
                        envvar_prefix, logging_level_from_secret_envvar
                    ),
                    "1",
                )
            )
        ):
            # Get log level from secrets
            log_level = None
            if "log" in self._secrets and "level" in self._secrets["log"]:
                log_level = self._secrets["log"]["level"].upper()

            if log_level:
                for logger_name in logging_config_yaml["loggers"]:
                    curr_logger = logging.getLogger(logger_name)
                    if log_setup:
                        self.setup_logger.debug(
                            App.create_static_log_message(
                                "6ba9367c",
                                f"Updated logger {logger_name} with level {log_level}",
                            )
                        )
                    for handler in curr_logger.handlers:
                        handler.setLevel(log_level)
                    curr_logger.setLevel(log_level)

    def _init_add_authentication_cfg(self, idps_config_file_envvar: str) -> None:
        """Add authentication configuration if file is provided."""
        logger = self.setup_logger
        msg = "Checking for authentication settings"
        logger.debug(App.create_static_log_message("d9dd9170", msg))

        # Check if IDPS config file is provided in environment
        idps_config_file = os.environ.get(idps_config_file_envvar)
        if not idps_config_file:
            msg = "No identity provider configuration file provided"
            logger.debug(App.create_static_log_message("e2547edf", msg))
            return

        if not Path(idps_config_file).is_file():
            msg = f"Authentication settings file does not exist: {idps_config_file}"
            logger.error(App.create_static_log_message("dc779cad", msg))
            raise FileNotFoundError(msg)
        else:
            with open(
                idps_config_file, "rt", encoding=getpreferredencoding()
            ) as handle:
                # Add IDPS_CONFIG to secrets for backward compatibility
                self._secrets["IDPS_CONFIG"] = json.load(handle)

    def _init_set_factories_for_services(self) -> None:
        """Set timestamp and ID factories for services."""
        # Set default factories
        timestamp_factory = getattr(
            TimestampFactory,
            self._settings.service.defaults.timestamp_factory,
        )
        id_factory = getattr(IdFactory, self._settings.service.defaults.id_factory)

        # Store factories in a way that's backward compatible
        self._secrets["service"] = self._secrets.get("service", {})
        self._secrets["service"]["defaults"] = {
            "timestamp_factory": timestamp_factory,
            "id_factory": id_factory,
        }

        # Set per-service factories
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()

            if service_type_str not in self._secrets["service"]:
                self._secrets["service"][service_type_str] = {}

            service_config = self._secrets["service"][service_type_str]

            # Use service-specific factory if configured, otherwise use default
            service_config["timestamp_factory"] = service_config.get(
                "timestamp_factory", timestamp_factory
            )
            service_config["id_factory"] = service_config.get("id_factory", id_factory)

    def _init_repository_cfg(self) -> None:
        """Initialize repository configuration with connection strings."""
        if "repository" not in self._secrets:
            return

        for repository_type in self.repository_type_enum:
            repository_type_str = repository_type.value.lower()

            # Handle 'dict' vs 'dict_repo' alias
            repo_key = (
                "dict_repo" if repository_type_str == "dict" else repository_type_str
            )
            if repo_key not in self._secrets["repository"]:
                repo_key = repository_type_str  # fallback to original key

            if repo_key not in self._secrets["repository"]:
                continue

            default_cfg = self._secrets["repository"][repo_key].get("defaults", {})

            for service_type in self._service_type_enum:
                service_type_str = service_type.value.lower()
                curr_cfg = self._secrets["repository"][repo_key]

                if service_type_str not in curr_cfg:
                    curr_cfg[service_type_str] = {}

                curr_cfg = curr_cfg[service_type_str]

                if repository_type_str in {"dict", "sa_sqlite"}:
                    parameter = "file"
                elif repository_type_str == "sa_sql":
                    parameter = "connection_string"
                else:
                    raise ValueError(f"Unknown repository type: {repository_type_str}")

                if parameter in curr_cfg:
                    format_string = curr_cfg[parameter]
                elif parameter in default_cfg:
                    format_string = default_cfg[parameter]
                else:
                    # No repository for this service
                    continue

                parameters = {
                    x: y for x, y in (default_cfg | curr_cfg).items() if x != parameter
                }

                if parameter == "connection_string":
                    if "pymssql" in parameters.get("driver", ""):
                        curr_cfg[parameter] = URL.create(
                            drivername=parameters["driver"],
                            host=parameters["server"],
                            database=parameters["database"],
                            username=parameters["uid"],
                            password=parameters["pwd"],
                        )
                    else:
                        sep = "="
                        conn_prefix, conn_details = format_string.format(
                            **parameters
                        ).split(sep, 1)
                        encoded_details = quote_plus(conn_details)
                        curr_cfg[parameter] = conn_prefix + sep + encoded_details
                else:
                    curr_cfg[parameter] = format_string.format(**parameters)
