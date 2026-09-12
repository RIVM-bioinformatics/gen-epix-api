"""Refactored configuration management using Strategy Pattern."""

import abc
import importlib
import logging
import logging.config as logging_config
import os
from enum import Enum
from locale import getpreferredencoding
from pathlib import Path

import yaml
from dynaconf import Dynaconf  # type: ignore[import-untyped]

from gen_epix.commondb.config.settings_manager import SettingsManager
from gen_epix.fastapp import App

# Third-party loggers that keep their configured level during global log-level updates.
_THIRD_PARTY_LOGGER_NAMES = {
    "sqlalchemy.engine",
    "sqlalchemy.pool",
    "httpx",
    "asyncio",
}
# Local logger suffixes that keep their configured level during global log-level updates.
_OWN_LOGGER_SUFFIXES = {
    "setup",
    "service",
    "app",
    "api",
    "external",
}
_LOG_LEVEL_DIAGNOSTIC_CODE = "8d4f29a1"

_NULL_LOGGER = logging.getLogger("null")
_NULL_LOGGER.addHandler(logging.NullHandler())
_NULL_LOGGER.setLevel(logging.CRITICAL + 1)  # above all standard levels
_NULL_LOGGER.propagate = False


def _is_descendant_logger(logger_name: str, parent_logger_name: str) -> bool:
    """Return True when logger_name is a child logger of parent_logger_name."""
    return logger_name.startswith(f"{parent_logger_name}.")


class BaseAppCfg(abc.ABC):
    """Encapsulates application configuration.

    This is a base class intended to be subclassed for specific applications.
    """

    def __init__(self) -> None:
        """Declare instance attributes; subclasses must assign them in their own __init__."""
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
        """Return this configuration instance's identifier.

        Returns:
            Configured instance identifier.

        Raises:
            ValueError: If the configuration has no assigned name.
        """
        if self._name is None:
            raise ValueError("name is not set")
        return self._name

    @property
    def app_name(self) -> str:
        """Name of the application (e.g. 'commondb', 'casedb')."""
        return self._app_name

    @property
    def service_type_enum(self) -> type[Enum]:
        """Enum class for the service types of this application."""
        return self._service_type_enum

    @property
    def repository_type_enum(self) -> type[Enum]:
        """Enum class for the repository types of this application."""
        return self._repository_type_enum

    @property
    def log_setup(self) -> bool:
        """Whether logging was configured during initialisation."""
        return self._log_setup

    @property
    def cfg(self) -> Dynaconf:
        """Loaded Dynaconf settings object."""
        return self._cfg

    @property
    def setup_logger(self) -> logging.Logger:
        """Logger used during application setup."""
        return self._setup_logger

    @property
    def api_logger(self) -> logging.Logger:
        """Logger for API layer messages."""
        return self._api_logger

    @property
    def app_logger(self) -> logging.Logger:
        """Logger for application layer messages."""
        return self._app_logger

    @property
    def service_logger(self) -> logging.Logger:
        """Logger for service layer messages."""
        return self._service_logger

    @abc.abstractmethod
    def copy_repository_files(
        self,
        tgt_dir: Path | str,
        service_type: Enum | None = None,
        on_exist: str = "skip",
    ) -> None:
        """
        Copy repository files to a new folder and update the configuration.

        correspondingly.

        Args:
            tgt_dir: Target directory for copied repository files.
            service_type: Optional service whose repository file is copied.
            on_exist: Behavior when the destination file already exists.

        Raises:
            NotImplementedError: Always; concrete configuration supplies copying.
        """
        raise NotImplementedError()


class AppCfg(BaseAppCfg):
    """Encapsulates the main application configuration class using Strategy Pattern."""

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
        name: str | None = None,
        envvar_prefix: str | None = None,
        settings_files: list[str] | None = None,
        log_any: bool = True,
        log_setup: bool = True,
        setup_logger_level: str | int | None = None,
        logger_prefix: str | None = None,
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
            envvar_prefix: Prefix for environment variables (defaults to app_name.upper())
            settings_files: List of settings files to load. No environment variables
               are used. If None, defaults and environment variables are used. Use this
               to have complete control over the configuration, e.g. for testing.
            log_any: Whether to set up any logging at all (if False, loggers are set to NullHandler)
            log_setup: Whether to set up logging
            logger_prefix: Prefix for logger names (defaults to app_name.lower())
            log_config_file_envvar: Environment variable for logging config file
            log_level_envvar: Environment variable to control log level
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
        self._settings_files = settings_files
        self._log_any = log_any
        self._log_setup = log_setup
        self._logger_prefix = logger_prefix or app_name.lower()
        self._log_config_file_envvar = log_config_file_envvar
        self._log_level_envvar = log_level_envvar
        self._setup_logger_level = setup_logger_level

        # Configure and set loggers
        self._init_configure_loggers()
        self.set_log_level(emit_diagnostic=False)
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
        if not self._log_any:
            self._setup_logger = _NULL_LOGGER
            self._api_logger = _NULL_LOGGER
            self._app_logger = _NULL_LOGGER
            self._service_logger = _NULL_LOGGER
            return
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
        settings_manager = SettingsManager(
            prefix=self._envvar_prefix, settings_files=self._settings_files
        )
        self._cfg = settings_manager.load_settings()

    def _init_validate_settings(self) -> None:
        """Validate settings and apply defaults to all services and repositories."""
        from gen_epix.commondb.domain.enum import (  # noqa: PLC0415
            IdFactory,
            TimestampFactory,
        )

        # Map timestamp and id factory strings to factory objects
        defaults_cfg = self._cfg["service"]["defaults"]["props"]
        defaults_cfg["timestamp_factory"] = getattr(
            TimestampFactory, defaults_cfg["timestamp_factory"]
        )
        defaults_cfg["id_factory"] = getattr(IdFactory, defaults_cfg["id_factory"])

        # Map default repository type string to enum member
        repository_type = getattr(
            self._repository_type_enum, self._cfg["repository"]["defaults"]["type"]
        )
        self._cfg["repository"]["defaults"]["type"] = repository_type

        # Apply defaults and dynamically import classes
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()

            # Ensure target service dict exists
            if service_type_str not in self._cfg["service"]:
                self._cfg["service"][service_type_str] = {}

            # Merge defaults with custom settings (custom values on the right override defaults)
            service_cfg = (
                self._cfg["service"]["defaults"]
                | self._cfg["service"][service_type_str]
            )

            # Get class for service
            service_module = service_cfg["module"]
            service_class_name = service_cfg["class_name"]
            service_cfg["class"] = getattr(
                importlib.import_module(service_module), service_class_name
            )
            self._cfg["service"][service_type_str] = service_cfg

            # Skip if the service does not have a repository
            if service_type_str not in self._cfg["repository"]:
                continue

            # Merge repository defaults with custom settings
            repository_cfg = (
                self._cfg["repository"]["defaults"]
                | self._cfg["repository"][service_type_str]
            )

            # Get class for repository
            repository_module = repository_cfg["module"]
            repository_class_name = repository_cfg["class_name"]
            repository_cfg["class"] = getattr(
                importlib.import_module(repository_module), repository_class_name
            )
            self._cfg["repository"][service_type_str] = repository_cfg

    def copy_repository_files(
        self,
        tgt_dir: Path | str,
        service_type: Enum | None = None,
        on_exist: str = "skip",
    ) -> None:
        """
        Copy repository files to a new folder and update the configuration.

        correspondingly. This is useful e.g. for creating isolated test environments.

        Args:
            tgt_dir: Existing target directory for copied repository files.
            service_type: Optional service whose repository file is copied.
            on_exist: Behavior when a destination file exists.

        Raises:
            ValueError: If the target is not a directory or ``on_exist`` is invalid.
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
        """Copy the repository file for one service type to tgt_dir."""
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
        """Copy a repository file while applying the destination-exists policy.

        Args:
            curr_path: Existing source repository file.
            new_path: Destination file to create or overwrite.
            on_exist: Behavior when the destination already exists.

        Raises:
            FileNotFoundError: If the source file does not exist.
            FileExistsError: If the destination exists and ``on_exist`` is ``raise``.
            NotImplementedError: If ``on_exist`` has an unsupported value.
        """
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

    def _resolve_log_level(
        self, log_level: str | int | None
    ) -> tuple[str | int | None, str, str, str | None, str | int | None]:
        """Resolve log level and report where it came from."""
        log_level_envvar = f"{self._envvar_prefix}{self._log_level_envvar}"
        env_value = os.environ.get(log_level_envvar)
        settings_value: str | int | None = None
        if hasattr(self, "_cfg"):
            try:
                settings_value = self._cfg["log"]["level"]  # type: ignore[index]
            except (KeyError, TypeError):
                settings_value = None

        source = "arg" if log_level is not None else "none"
        resolved_level = log_level
        if resolved_level is None and env_value is not None:
            resolved_level = env_value
            source = "env"
        elif resolved_level is None and settings_value is not None:
            resolved_level = settings_value
            source = "settings"

        if isinstance(resolved_level, str):
            resolved_level = resolved_level.upper()

        return resolved_level, source, log_level_envvar, env_value, settings_value

    def _set_known_handlers_to_notset(self) -> None:
        """Normalise shared handlers; level filtering is controlled by loggers."""
        seen_handler_ids: set[int] = set()
        logger_names = set(self._logging_config_yaml.get("loggers", {}).keys())
        for logger_attr in (
            "_setup_logger",
            "_api_logger",
            "_app_logger",
            "_service_logger",
        ):
            logger_obj = getattr(self, logger_attr, None)
            logger_name = getattr(logger_obj, "name", None)
            if isinstance(logger_name, str):
                logger_names.add(logger_name)

        for logger_name in logger_names:
            for handler in logging.getLogger(logger_name).handlers:
                handler_id = id(handler)
                if handler_id in seen_handler_ids:
                    continue
                handler.setLevel(logging.NOTSET)
                seen_handler_ids.add(handler_id)

        for handler in logging.getLogger().handlers:
            handler_id = id(handler)
            if handler_id in seen_handler_ids:
                continue
            handler.setLevel(logging.NOTSET)
            seen_handler_ids.add(handler_id)

    def _emit_log_level_diagnostic(
        self,
        resolved_level: str | int | None,
        source: str,
        env_var_name: str,
        env_var_value: str | None,
        settings_value: str | int | None,
    ) -> None:
        """Emit a structured info log describing the active log level and its source."""
        if not self._log_setup:
            return
        self.setup_logger.info(
            App.create_static_log_message(
                _LOG_LEVEL_DIAGNOSTIC_CODE,
                "APPLIED_LOG_LEVEL",
                resolved_level=resolved_level,
                source=source,
                env_var_name=env_var_name,
                env_var_value=env_var_value,
                settings_value=settings_value,
            )
        )

    def set_log_level(
        self, log_level: str | int | None = None, emit_diagnostic: bool = True
    ) -> None:
        """Set log level for all loggers."""
        if not self._log_any:
            return
        (
            resolved_level,
            source,
            env_var_name,
            env_var_value,
            settings_value,
        ) = self._resolve_log_level(log_level)
        if resolved_level is None:
            if emit_diagnostic:
                self._emit_log_level_diagnostic(
                    resolved_level,
                    source,
                    env_var_name,
                    env_var_value,
                    settings_value,
                )
            # No log level available
            return

        # Set new log level for all in settings as well
        if hasattr(self, "_cfg"):
            self._cfg["log"]["level"] = resolved_level  # type: ignore[index]
        self._set_known_handlers_to_notset()
        self._setup_logger.setLevel(resolved_level)
        logger_names = set(_THIRD_PARTY_LOGGER_NAMES)
        logger_names.update(
            AppCfg._prefix_logger(self._logger_prefix, x) for x in _OWN_LOGGER_SUFFIXES
        )
        for logger_name, logger_cfg in self._logging_config_yaml["loggers"].items():
            assert isinstance(logger_cfg, dict)
            curr_logger = logging.getLogger(logger_name)
            if self._log_setup:
                self.setup_logger.debug(
                    App.create_static_log_message(
                        "6ba9367c",
                        f"Updated logger {logger_name} with level {resolved_level}",
                    )
                )
            # If the logger is in the config, use its level if specified, otherwise use the resolved level. If the logger is not in the config, use the resolved level.
            effective_level = resolved_level
            if logger_name in logger_names:
                effective_level = logger_cfg.get("level", resolved_level)
            curr_logger.setLevel(effective_level)

        # Keep runtime child loggers of pinned third-party namespaces pinned as well.
        runtime_logger_names = sorted(logging.root.manager.loggerDict.keys())
        for runtime_logger_name in runtime_logger_names:
            for pinned_logger_name in _THIRD_PARTY_LOGGER_NAMES:
                if not _is_descendant_logger(runtime_logger_name, pinned_logger_name):
                    continue
                pinned_level = (
                    self._logging_config_yaml["loggers"]
                    .get(pinned_logger_name, {})
                    .get("level", resolved_level)
                )
                logging.getLogger(runtime_logger_name).setLevel(pinned_level)
                break

        if emit_diagnostic:
            self._emit_log_level_diagnostic(
                resolved_level,
                source,
                env_var_name,
                env_var_value,
                settings_value,
            )
