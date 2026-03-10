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

import yaml  # type: ignore[import-untyped]
from dynaconf import Dynaconf

from gen_epix.commondb.config.factory import IdFactory, TimestampFactory
from gen_epix.commondb.config.settings_manager import SettingsManager
from gen_epix.fastapp import App

_PINNED_THIRD_PARTY_LOGGERS = {
    "sqlalchemy.engine",
    "sqlalchemy.pool",
    "httpx",
    "asyncio",
}
_PINNED_LOCAL_LOGGER_SUFFIXES = {
    "setup",
    "service",
    "app",
    "api",
    "external",
}


def _is_descendant_logger(logger_name: str, parent_logger_name: str) -> bool:
    """Return True when logger_name is a child logger of parent_logger_name."""
    return logger_name.startswith(f"{parent_logger_name}.")


class BaseAppCfg(abc.ABC):
    """Abstract base class for application configuration."""

    def __init__(self) -> None:
        self._name: str | None
        self._app_name: str
        self._service_type_enum: type[Enum]
        self._repository_type_enum: type[Enum]
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
    def service_type_enum(self) -> type[Enum]:
        return self._service_type_enum

    @property
    def repository_type_enum(self) -> type[Enum]:
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
        service_type_enum: type[Enum],
        repository_type_enum: type[Enum],
        log_setup: bool = True,
        name: str | None = None,
        setup_logger_level: str | int | None = None,
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

        # Add some properties
        self._app_name = app_name
        self._name = name
        self._service_type_enum = service_type_enum
        self._repository_type_enum = repository_type_enum
        self._envvar_prefix = envvar_prefix or f"{app_name.upper()}_"
        self._logger_prefix = logger_prefix or app_name.lower()
        self._log_config_file_envvar = log_config_file_envvar
        self._log_setup = log_setup
        self._log_level_envvar = log_level_envvar
        self._setup_logger_level = setup_logger_level

        # Configure and set loggers
        self._init_configure_loggers()
        self.set_log_level()
        if self._setup_logger_level is not None:
            self.setup_logger.setLevel(self._setup_logger_level)
        if self._log_setup:
            self.setup_logger.info(
                App.create_static_log_message("c6010f14", "Started loading config data")
            )

        # Load settings
        self._init_load_settings()
        self.set_log_level()
        if self._log_setup:
            self.setup_logger.info(
                App.create_static_log_message(
                    "a7b3c4d5", f"Loaded settings from {type(self._cfg).__name__}"
                )
            )

        # Validate settings
        self._init_validate_settings()
        if self._log_setup:
            self.setup_logger.info(
                App.create_static_log_message(
                    "cdb7abcb", "Finished loading config data"
                )
            )

    def _init_configure_loggers(
        self,
    ) -> None:
        """Configure loggers from logging configuration file."""
        logging_config_file = os.environ[
            f"{self._envvar_prefix}{self._log_config_file_envvar}"
        ]
        with open(logging_config_file, "rt", encoding=getpreferredencoding()) as handle:
            logging_config_yaml = yaml.safe_load(handle.read())
            logging_config.dictConfig(logging_config_yaml)

        # Get loggers and put as attributes
        self._setup_logger = logging.getLogger(
            AppCfg._prefix_logger(self._logger_prefix, "setup")
        )
        self._api_logger = logging.getLogger(
            AppCfg._prefix_logger(self._logger_prefix, "api")
        )
        self._app_logger = logging.getLogger(
            AppCfg._prefix_logger(self._logger_prefix, "app")
        )
        self._service_logger = logging.getLogger(
            AppCfg._prefix_logger(self._logger_prefix, "service")
        )
        self._logging_config_yaml = logging_config_yaml

    def _init_load_settings(self) -> None:
        """Load settings using SettingsManager."""

        settings_manager = SettingsManager(prefix=self._envvar_prefix)
        self._cfg = settings_manager.load_settings()

    def _init_validate_settings(self) -> None:
        """Validate settings and apply defaults to all services and repositories."""
        # Map timestamp and id factories
        defaults_cfg = self._cfg["service"]["defaults"]["props"]
        timestamp_factory = getattr(
            TimestampFactory,
            defaults_cfg["timestamp_factory"],
        )
        id_factory = getattr(IdFactory, defaults_cfg["id_factory"])
        defaults_cfg["timestamp_factory"] = timestamp_factory
        defaults_cfg["id_factory"] = id_factory

        # Map default repository type
        repository_type = getattr(
            self._repository_type_enum, self._cfg["repository"]["defaults"]["type"]
        )
        self._cfg["repository"]["defaults"]["type"] = repository_type

        # Get class for and apply defaults to each service and repository
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()
            if service_type_str not in self._cfg["service"]:
                self._cfg["service"].update({service_type_str: {}})
            service_cfg = self._cfg["service"][service_type_str]

            # Get class for service
            service_module = service_cfg["module"]
            service_class_name = service_cfg["class_name"]
            service_cfg["class"] = getattr(
                importlib.import_module(service_module), service_class_name
            )

            # Apply defaults to service
            orig_cfg = copy.deepcopy(service_cfg)
            service_cfg.update(self._cfg["service"]["defaults"])
            service_cfg.update(orig_cfg)

            # Skip if the service does not have a repository
            if service_type_str not in self._cfg["repository"]:
                continue
            repository_cfg = self._cfg["repository"][service_type_str]

            # Get class for repository
            repository_module = repository_cfg["module"]
            repository_class_name = repository_cfg["class_name"]
            repository_cfg["class"] = getattr(
                importlib.import_module(repository_module), repository_class_name
            )

            # Apply defaults to repository, if the service has a repository
            orig_cfg = copy.deepcopy(repository_cfg)
            repository_cfg.update(self._cfg["repository"]["defaults"])
            repository_cfg.update(orig_cfg)

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
            self._copy_single_repository_file(service_type, tgt_dir, on_exist)

    def _copy_single_repository_file(
        self, service_type: Enum, tgt_dir: Path | str, on_exist: str
    ) -> None:
        service_type_str = service_type.value.lower()
        if service_type_str not in self._cfg["repository"]:
            return
        cfg = self._cfg["repository"][service_type_str]["props"]
        if "file" not in cfg:
            return
        curr_path = Path(cfg["file"])
        tgt_dir_path = tgt_dir if isinstance(tgt_dir, Path) else Path(tgt_dir)
        new_path = tgt_dir_path / curr_path.name

        # Copy file
        self._handle_file_copy(curr_path, new_path, on_exist)
        cfg["file"] = str(tgt_dir_path / curr_path.name)

    def _handle_file_copy(self, curr_path: Path, new_path: Path, on_exist: str) -> None:
        if not curr_path.exists():
            raise FileNotFoundError(f"Source file not found: {curr_path}")
        if new_path.exists():
            if on_exist == "overwrite":
                pass
            elif on_exist == "skip":
                return
            elif on_exist == "raise":
                raise FileExistsError(f"Destination file already exists: {new_path}")
            else:
                raise NotImplementedError(
                    f"on_exist value '{on_exist}' not implemented"
                )
        with open(curr_path, "rb") as src_handle:
            with open(new_path, "wb") as dst_handle:
                dst_handle.write(src_handle.read())

    def set_log_level(self, log_level: str | int | None = None) -> None:
        """Set log level for all loggers."""
        # Parse log level
        log_level_envvar = f"{self._envvar_prefix}{self._log_level_envvar}"
        if log_level is None:
            if log_level_envvar in os.environ:
                # Get log level from environment variable, before settings
                log_level = os.environ[log_level_envvar]
            elif hasattr(self, "_cfg"):
                # Get log level from settings, if available
                log_level = self._cfg["log"]["level"]
        if log_level is None:
            # No log level available
            return
        if isinstance(log_level, str):
            log_level = log_level.upper()
        # Set new log level for all in settings as well
        if hasattr(self, "_cfg"):
            self._cfg["log"]["level"] = log_level
        for handler in self._setup_logger.handlers:
            handler.setLevel(log_level)
        self._setup_logger.setLevel(log_level)
        pinned_logger_names = set(_PINNED_THIRD_PARTY_LOGGERS)
        pinned_logger_names.update(
            AppCfg._prefix_logger(self._logger_prefix, x)
            for x in _PINNED_LOCAL_LOGGER_SUFFIXES
        )
        for logger_name, logger_cfg in self._logging_config_yaml["loggers"].items():
            assert isinstance(logger_cfg, dict)
            curr_logger = logging.getLogger(logger_name)
            if self._log_setup:
                self.setup_logger.debug(
                    App.create_static_log_message(
                        "6ba9367c",
                        f"Updated logger {logger_name} with level {log_level}",
                    )
                )
            effective_level = log_level
            if logger_name in pinned_logger_names:
                effective_level = logger_cfg.get("level", log_level)
            for handler in curr_logger.handlers:
                handler.setLevel(effective_level)
            curr_logger.setLevel(effective_level)

        # Keep runtime child loggers of pinned third-party namespaces pinned as well.
        runtime_logger_names = sorted(logging.root.manager.loggerDict.keys())
        for runtime_logger_name in runtime_logger_names:
            for pinned_logger_name in _PINNED_THIRD_PARTY_LOGGERS:
                if not _is_descendant_logger(runtime_logger_name, pinned_logger_name):
                    continue
                pinned_level = (
                    self._logging_config_yaml["loggers"]
                    .get(pinned_logger_name, {})
                    .get("level", log_level)
                )
                logging.getLogger(runtime_logger_name).setLevel(pinned_level)
                break
