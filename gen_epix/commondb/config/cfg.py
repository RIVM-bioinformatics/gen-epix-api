"""Refactored configuration management using Strategy Pattern."""

import abc
import copy
import importlib
import logging
import logging.config as logging_config
import os
from enum import Enum
from locale import getpreferredencoding
from pathlib import Path
from typing import Type

import yaml  # type: ignore[import-untyped]
from dynaconf import Dynaconf

from gen_epix.commondb.config.factory import IdFactory, TimestampFactory
from gen_epix.commondb.config.settings_manager import SettingsManager
from gen_epix.fastapp import App


class BaseAppCfg(abc.ABC):
    """Abstract base class for application configuration."""

    def __init__(self) -> None:
        self._name: str | None
        self._app_name: str
        self._service_type_enum: Type[Enum]
        self._repository_type_enum: Type[Enum]
        self._log_setup: bool
        self._cfg: Dynaconf
        self._setup_logger: logging.Logger
        self._api_logger: logging.Logger
        self._app_logger: logging.Logger
        self._service_logger: logging.Logger

    @property
    def name(self) -> str:
        if self._name is None:
            raise ValueError("name is not set")
        return self._name

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
    def cfg(self) -> Dynaconf:
        return self._cfg

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

    @abc.abstractmethod
    def copy_repository_files(
        self,
        tgt_dir: Path | str,
        service_type: Enum | None = None,
        on_exist: str = "skip",
    ) -> None:
        raise NotImplementedError("Subclasses must implement copy_repository_files")


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
        app_name_or_enum: Enum | str,
        service_type_enum: Type[Enum],
        repository_type_enum: Type[Enum],
        log_setup: bool = True,
        name: str | None = None,
        setup_logger_level: int | None = None,
        logger_prefix: str | None = None,
        envvar_prefix: str | None = None,
        log_config_file_envvar: str = "LOG_CONFIG_FILE",
        log_level_envvar: str = "LOG_LEVEL",
    ):
        """Initialize application configuration.

        Args:
            app_name: Name of the application (e.g., 'commondb', 'casedb')
            service_type_enum: Enum of service types
            repository_type_enum: Enum of repository types
            name: optional name for this configuration instance that can e.g. be used
               as a key in collection of configurations
            log_setup: Whether to set up logging
            logger_prefix: Prefix for logger names (defaults to app_name.lower())
            envvar_prefix: Prefix for environment variables (defaults to app_name.upper())
            logging_config_file_envvar: Environment variable for logging config file
            idps_config_file_envvar: Environment variable for identity provider config
            logging_level_from_secret_envvar: Environment variable to control log level from secrets
        """
        # Parse input
        if isinstance(app_name_or_enum, Enum):
            app_name = str(app_name_or_enum.value)
        else:
            app_name = app_name_or_enum
        logger_prefix = logger_prefix or app_name.lower()
        envvar_prefix = envvar_prefix or f"{app_name.upper()}_"

        # Add some properties
        self._app_name = app_name
        self._name = name
        self._service_type_enum = service_type_enum
        self._repository_type_enum = repository_type_enum
        self._log_setup = log_setup

        # Configure and set loggers
        self._init_configure_loggers(
            envvar_prefix, log_config_file_envvar, logger_prefix
        )
        if setup_logger_level is not None:
            self.setup_logger.setLevel(setup_logger_level)
        if log_setup:
            self.setup_logger.info(
                App.create_static_log_message("c6010f14", "Started loading config data")
            )

        # Load settings
        self._init_load_settings(envvar_prefix, log_setup)

        # Validate settings
        self._init_validate_settings()

        # Finalise process
        if log_setup:
            self.setup_logger.info(
                App.create_static_log_message(
                    "cdb7abcb", "Finished loading config data"
                )
            )

        # Set log level
        self._init_set_log_level(envvar_prefix, log_level_envvar, log_setup)

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
        self._cfg = settings_manager.load_settings()

        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "a7b3c4d5", f"Loaded settings from {type(self._cfg).__name__}"
                )
            )

    def _init_validate_settings(self) -> None:
        """Validate settings and apply defaults to all services and repositories."""
        # Map timestamp and id factories
        timestamp_factory = getattr(
            TimestampFactory,
            self._cfg["service"]["defaults"]["props"]["timestamp_factory"],
        )
        id_factory = getattr(
            IdFactory, self._cfg["service"]["defaults"]["props"]["id_factory"]
        )
        self._cfg["service"]["defaults"]["props"][
            "timestamp_factory"
        ] = timestamp_factory
        self._cfg["service"]["defaults"]["props"]["id_factory"] = id_factory

        # Map default repository type
        repository_type = getattr(
            self._repository_type_enum, self._cfg["repository"]["defaults"]["type"]
        )
        self._cfg["repository"]["defaults"]["type"] = repository_type

        # Get class for and apply defaults to each service and repository
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()

            # Get class for service
            service_module = self._cfg["service"][service_type_str]["module"]
            service_class_name = self._cfg["service"][service_type_str]["class_name"]
            self._cfg["service"][service_type_str]["class"] = getattr(
                importlib.import_module(service_module), service_class_name
            )

            # Apply defaults to service
            if service_type_str not in self._cfg["service"]:
                self._cfg["service"].update({service_type_str: {}})
            orig_cfg = copy.deepcopy(self._cfg["service"][service_type_str])
            self._cfg["service"][service_type_str].update(
                self._cfg["service"]["defaults"]
            )
            self._cfg["service"][service_type_str].update(orig_cfg)

            # Skip if the service does not have a repository
            if service_type_str not in self._cfg["repository"]:
                continue

            # Get class for repository
            repository_module = self._cfg["repository"][service_type_str]["module"]
            repository_class_name = self._cfg["repository"][service_type_str][
                "class_name"
            ]
            self._cfg["repository"][service_type_str]["class_name"] = getattr(
                importlib.import_module(repository_module), repository_class_name
            )

            # Apply defaults to repository, if the service has a repository
            orig_cfg = copy.deepcopy(self._cfg["repository"][service_type_str])
            self._cfg["repository"][service_type_str].update(
                self._cfg["repository"]["defaults"]
            )
            self._cfg["repository"][service_type_str].update(orig_cfg)

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
            # Get log level
            log_level = None
            if "log" in self._cfg and "level" in self._cfg["log"]:
                log_level = self._cfg["log"]["level"].upper()

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

    def copy_repository_files(
        self,
        tgt_dir: Path | str,
        service_type: Enum | None = None,
        on_exist: str = "skip",
    ) -> None:
        """
        Copy any repository files to a new folder and update the configuration
        correspondingly. This is useful e.g. for creating isolated test environments.
        """
        # Parse input
        if isinstance(tgt_dir, str):
            tgt_dir = Path(tgt_dir)
        if not tgt_dir.is_dir():
            raise ValueError(f"new_folder {tgt_dir} is not a directory")
        if on_exist not in ("skip", "overwrite", "raise"):
            raise ValueError(
                f"on_exist must be 'skip', 'overwrite' or 'raise', got {on_exist}"
            )
        if service_type is None:
            service_types = list(self.service_type_enum)
        else:
            service_types = [service_type]
        # Go over each service type
        for service_type in service_types:
            # Get file path from config
            service_type_str = service_type.value.lower()
            if service_type_str not in self._cfg["repository"]:
                continue
            cfg = self._cfg["repository"][service_type_str]["props"]
            if "file" not in cfg:
                continue
            curr_path = Path(cfg["file"])
            new_path = tgt_dir / curr_path.name
            # Copy file
            if not curr_path.exists():
                raise FileNotFoundError(f"Source file not found: {curr_path}")
            if new_path.exists():
                if on_exist == "overwrite":
                    pass
                elif on_exist == "skip":
                    continue
                elif on_exist == "raise":
                    raise FileExistsError(
                        f"Destination file already exists: {new_path}"
                    )
                else:
                    raise NotImplementedError(
                        f"on_exist value '{on_exist}' not implemented"
                    )
            with open(curr_path, "rb") as src_handle:
                with open(new_path, "wb") as dst_handle:
                    dst_handle.write(src_handle.read())
            # Update config
            cfg["file"] = str(Path(tgt_dir) / curr_path.name)
