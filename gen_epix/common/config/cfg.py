import abc
import json
import logging.config as logging_config
import os
from enum import Enum
from locale import getpreferredencoding
from pathlib import Path
from typing import Any, Type
from urllib.parse import quote_plus

import yaml
from dynaconf import Dynaconf
from sqlalchemy import URL
from uvicorn.logging import logging

from gen_epix.common.config.factory import IdFactory, TimestampFactory
from gen_epix.common.util import update_cfg_from_file
from gen_epix.fastapp import App


class BaseAppCfg(abc.ABC):
    def __init__(self) -> None:
        self._app_name: str
        self._service_type_enum: Type[Enum]
        self._repository_type_enum: Type[Enum]
        self._log_setup: bool
        self._cfg: Any
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
    def cfg(self) -> Any:
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


class AppCfg(BaseAppCfg):
    @staticmethod
    def _prefix_envvar(
        envvar_prefix: str | None, envvar: str, delimiter: str = "_"
    ) -> str:
        if envvar_prefix:
            return f"{envvar_prefix}{delimiter}{envvar}"
        return envvar

    @staticmethod
    def _prefix_logger(
        logger_prefix: str | None, logger_name: str, delimiter: str = "."
    ) -> str:
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
        settings_dir_envvar: str = "SETTINGS_DIR",
        secrets_dir_envvar: str | None = "SECRETS_DIR",
        logging_config_file_envvar: str = "LOGGING_CONFIG_FILE",
        idps_config_file_envvar: str = "IDPS_CONFIG_FILE",
        logging_level_from_secret_envvar: str = "LOGGING_LEVEL_FROM_SECRET",
        settings_files: list[str] | None = None,
        cfg_key_map: dict[str, str] | None = None,
    ):
        # Parse input
        if logger_prefix is None:
            logger_prefix = app_name.lower()
        if envvar_prefix is None:
            envvar_prefix = app_name.upper()
        if settings_files is None:
            settings_files = [
                "settings.toml",
                "secrets.default.toml",
            ]
        if cfg_key_map is None:
            cfg_key_map = {
                "automaticnewuser": "automatic_new_user",
                "sasql": "sa_sql",
                "sasqlite": "sa_sqlite",
            }

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
                    "c6010f14", "Starting setting up config data"
                )
            )

        # Read and set initial config data
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message("d5fd558a", "Reading initial config data")
            )
        self._init_read_config_data(envvar_prefix, settings_dir_envvar, settings_files)

        # Set timestamp and ID factory per service
        self._init_set_factories_for_services()

        # Add secrets
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "c61368d6", "Updating config with secrets"
                )
            )
        self._init_add_secrets(secrets_dir_envvar, cfg_key_map)

        # Set log level
        self._init_set_log_level(
            envvar_prefix, logging_level_from_secret_envvar, log_setup
        )

        # Add authentication settings
        self._init_add_authentication_cfg(idps_config_file_envvar)

        # Fill in repository connection string parameters per service, taking either the
        # parameters from the service or otherwise the defaults
        self._init_repository_cfg()

        # Finalise process
        if log_setup:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "cdb7abcb", "Finished setting up config data"
                )
            )

    def _init_configure_loggers(
        self,
        envvar_prefix: str | None,
        logging_config_file_envvar: str,
        logger_prefix: str | None,
    ) -> None:
        # Configure loggers
        logging_config_file = os.environ[
            AppCfg._prefix_envvar(envvar_prefix, logging_config_file_envvar)
        ]
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

    def _init_read_config_data(
        self,
        envvar_prefix: str | None,
        settings_dir_envvar: str,
        settings_files: list[str],
    ) -> None:
        settings_dir = Path(
            os.environ[AppCfg._prefix_envvar(envvar_prefix, settings_dir_envvar)]
        )
        if not settings_dir.is_dir():
            msg = f"Settings directory does not exist: {settings_dir}"
            self._setup_logger.error(App.create_static_log_message("e0d6f1d2", msg))
            raise FileNotFoundError(msg)
        settings_full_files = [settings_dir / x for x in settings_files]
        invalid_files = [x for x in settings_full_files if not x.is_file()]
        if invalid_files:
            invalid_files_str = ", ".join(invalid_files)
            msg = f"Some settings files do not exist: {invalid_files_str}"
            self._setup_logger.error(App.create_static_log_message("a81c4c69", msg))
            raise FileNotFoundError(msg)
        cfg = Dynaconf(
            envvar_prefix=envvar_prefix,
            settings_files=settings_full_files,
        )

        # Set as attribute
        self._cfg = cfg

    def _init_set_log_level(
        self,
        envvar_prefix: str | None,
        logging_level_from_secret_envvar: str,
        log_setup: bool,
    ) -> logging.Logger:
        cfg = self._cfg
        logger = self._setup_logger
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
            for logger_name in logging_config_yaml["loggers"]:
                curr_logger = logging.getLogger(logger_name)
                if log_setup:
                    logger.debug(
                        App.create_static_log_message(
                            "6ba9367c",
                            f"Updated logger {logger_name} with level {cfg.secret['log']['level']}",
                        )
                    )
                for handler in curr_logger.handlers:
                    handler.setLevel(cfg.secret["log"]["level"])
                curr_logger.setLevel(cfg.secret["log"]["level"])
        return curr_logger

    def _init_add_authentication_cfg(self, idps_config_file_envvar: str) -> None:
        cfg = self._cfg
        logger = self._setup_logger
        msg = "Updating config with authentication settings"
        logger.debug(App.create_static_log_message("d9dd9170", msg))
        if idps_config_file_envvar not in cfg:
            msg = "No identity provider configuration file provided"
            logger.error(App.create_static_log_message("e2547edf", msg))
            raise FileNotFoundError(msg)
        idps_config_file = cfg.get(idps_config_file_envvar)
        if not Path(idps_config_file).is_file():
            msg = f"Authentication settings file does not exist: {idps_config_file}"
            logger.error(App.create_static_log_message("dc779cad", msg))
            raise FileNotFoundError(msg)
        else:
            with open(
                idps_config_file, "rt", encoding=getpreferredencoding()
            ) as handle:
                cfg.IDPS_CONFIG = json.load(handle)

    def _init_set_factories_for_services(self) -> None:
        cfg = self._cfg
        cfg.service.defaults.timestamp_factory = getattr(
            TimestampFactory,
            cfg.service.defaults.get("timestamp_factory", "DATETIME_NOW"),
        )
        cfg.service.defaults.id_factory = getattr(
            IdFactory, cfg.service.defaults.get("id_factory", "UUID4")
        )
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()
            if service_type_str not in cfg.service:
                cfg.service[service_type_str] = {}
            if "timestamp_factory" in cfg.service[service_type_str]:
                cfg.service[service_type_str]["timestamp_factory"] = getattr(
                    TimestampFactory,
                    cfg.service[service_type_str].get("timestamp_factory"),
                )
            else:
                cfg.service[service_type_str][
                    "timestamp_factory"
                ] = cfg.service.defaults.timestamp_factory
            if "id_factory" in cfg.service[service_type_str]:
                cfg.service[service_type_str]["id_factory"] = getattr(
                    TimestampFactory, cfg.service[service_type_str].get("id_factory")
                )
            else:
                cfg.service[service_type_str][
                    "id_factory"
                ] = cfg.service.defaults.id_factory

    def _init_add_secrets(
        self, secrets_dir_envvar: str | None, cfg_key_map: dict[str, str] | None
    ) -> None:
        cfg = self._cfg
        logger = self._setup_logger
        if secrets_dir_envvar is None:
            self.setup_logger.debug(
                App.create_static_log_message(
                    "e6f4f86d", "Config is NOT updated with secrets"
                )
            )
        else:
            secrets_dir = cfg.get(secrets_dir_envvar)
            if secrets_dir:
                if not Path(secrets_dir).is_dir():
                    msg = f"Secrets directory does not exist: {secrets_dir}"
                    logger.error(App.create_static_log_message("d7190d85", msg))
                    raise FileNotFoundError(msg)
                update_cfg_from_file(cfg["secret"], secrets_dir, cfg_key_map)
            else:
                msg = "Secrets directory not provided, proceeding with default"
                logger.warning(App.create_static_log_message("e97a9639", msg))
        cfg.secret["db"]["repository_type"] = self.repository_type_enum[
            cfg.secret["db"]["repository_type"]
        ]
        cfg.secret["log"]["level"] = cfg.secret["log"]["level"].upper()

    def _init_repository_cfg(self) -> None:
        cfg = self._cfg
        for repository_type in self.repository_type_enum:
            repository_type_str = repository_type.value.lower()
            default_cfg = cfg["secret"]["repository"][repository_type_str].get(
                "defaults", {}
            )
            for service_type in self._service_type_enum:
                service_type_str = service_type.value.lower()
                curr_cfg = cfg["secret"]["repository"][repository_type_str]
                if service_type_str not in curr_cfg:
                    curr_cfg[service_type_str] = {}
                curr_cfg = curr_cfg[service_type_str]
                if repository_type_str in {"dict", "sa_sqlite"}:
                    parameter = "file"
                elif repository_type_str in {"sa_sql"}:
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
                    if "pymssql" in parameters["driver"]:
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
