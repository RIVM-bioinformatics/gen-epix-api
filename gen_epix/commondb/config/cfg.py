"""Refactored configuration management using Strategy Pattern."""

import abc
import copy
import importlib
import logging
import logging.config as logging_config
import os
import re
from enum import Enum
from fnmatch import fnmatchcase
from locale import getpreferredencoding
from pathlib import Path
from typing import Any, cast

import yaml
from dynaconf import Dynaconf, Validator  # type: ignore[import-untyped]

from gen_epix.commondb.config import cfg_types
from gen_epix.commondb.config.settings_manager import SettingsManager
from gen_epix.fastapp import App, exc

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


def convert_to_bool(value: Any) -> tuple[bool, bool]:
    """Convert a value to boolean when possible.

    Config values often arrive as strings (e.g. "0" from envsubst-rendered
    TOML), so bool-like strings are accepted alongside real booleans.

    Returns a tuple of ``(success, converted_value)``.
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


_NULL_LOGGER = logging.getLogger("null")
_NULL_LOGGER.addHandler(logging.NullHandler())
_NULL_LOGGER.setLevel(logging.CRITICAL + 1)  # above all standard levels
_NULL_LOGGER.propagate = False

_STANDARD_LOG_LEVELS: tuple[str, ...] = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

# Every repository entry's connection_string under the SA_SQL default has this
# same value, built by interpolating repository.defaults.props at read time;
# defined once here and referenced by every repo entry in _DEFAULT_SETTINGS
# below, rather than repeated per repo.
_SA_SQL_CONNECTION_STRING = (
    "@format mssql+pyodbc:///?odbc_connect="
    "DRIVER={this.repository.defaults.props.driver};"
    "SERVER={this.repository.defaults.props.server};"
    "DATABASE={this.repository.defaults.props.database};"
    "UID={this.repository.defaults.props.uid};"
    "PWD={this.repository.defaults.props.pwd}{this.repository.defaults.props.other}"
)

# Matches a blank PWD segment in a resolved SA_SQL connection string.
_BLANK_PWD_IN_CONNECTION_STRING = re.compile(r"PWD=(;|$)")


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

    # Baseline business-config values for the commondb app. Every other
    # app's AppCfg subclass deep-merges its own deltas on top of this dict.
    # A key set here and left unmentioned by a subclass keeps this value.
    #
    # This is the lowest-precedence layer of the configuration:
    # SettingsManager passes it to Dynaconf as constructor keyword
    # arguments, which Dynaconf treats as a base layer that any matching key
    # in a settings file overrides, and any matching environment variable
    # overrides in turn. This holds recursively for nested keys: a settings
    # file that sets only service.auth.props.root.user.key leaves every
    # sibling key under service.auth.props sourced from this dict.
    #
    # "feature_flags" is intentionally absent from this literal — see
    # _get_default_settings below.
    _DEFAULT_SETTINGS: dict[str, Any] = {
        "app": {"host": "0.0.0.0", "debug": False, "port": 8010},
        "api": {
            "default_route": "/openapi.json",
            "gzip_response_minimum_size": 1024,
            "http_header": {
                "general": {
                    "CacheControl": "no-cache, no-store",
                    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; sandbox",
                    "Content-Security-Policy-Report-Only": "default-src 'none'; frame-ancestors 'none'; sandbox",
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Expires": "0",
                    "Pragma": "no-cache",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                },
                "openapi": {
                    "CacheControl": "no-cache, no-store",
                    "Expires": "0",
                    "Pragma": "no-cache",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                },
                "auth": {
                    "CacheControl": "no-cache, no-store",
                    "Expires": "0",
                    "Pragma": "no-cache",
                    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                },
            },
            "route": {"v1": "/v1"},
        },
        "log": {
            "level": "INFO",
            "command_object_summarization": {
                "enabled": True,
                "max_list_items": 3,
                "max_string_length": 500,
                "max_exception_message_length": 2000,
            },
        },
        "service": {
            "defaults": {
                "props": {"timestamp_factory": "DATETIME_NOW", "id_factory": "UUID4"},
            },
            "abac": {
                "module": "gen_epix.commondb.services",
                "class_name": "AbacService",
            },
            "auth": {
                "module": "gen_epix.commondb.services",
                "class_name": "AuthService",
                "props": {
                    "auto_create_new_users": False,
                    "root_token_time_to_live": 0,  # disabled during development
                    "auto_created_user": {
                        "organization_id": "018d074d-ea0c-e942-07db-a3cc0ba1d653",
                        "roles": ["COMMONDB_ORG_USER"],
                    },
                    "root": {
                        "organization": {
                            "id": "018d074d-ea0c-e942-07db-a3cc0ba1d653",
                            "code": "DUMMY",
                            "name": "DUMMY",
                        },
                        "user": {"key": "root@dummy.org"},
                    },
                },
            },
            "organization": {
                "module": "gen_epix.commondb.services",
                "class_name": "OrganizationService",
            },
            "rbac": {
                "module": "gen_epix.commondb.services",
                "class_name": "RbacService",
                "props": {
                    "user_invitation_time_to_live": 604800
                },  # one week, in seconds
            },
            "system": {
                "module": "gen_epix.commondb.services",
                "class_name": "SystemService",
            },
        },
        # SA_SQL is the baseline repository backend: a deployment that never
        # sets DevRepositoryConfig away from SA_SQL needs no repository file
        # at all. driver/server/database/other are safe, non-secret defaults
        # (server/database match the standard local/test SQL Server
        # container). uid/pwd are deliberately blank: a Dynaconf settings
        # object built from a defaults dict passed as constructor kwargs
        # (as SettingsManager does) cannot have a brand-new nested key
        # injected via an environment variable later — only an *existing*
        # key can be overridden that way — so uid/pwd must stay present
        # here (as an unambiguous, never-real placeholder) for an env var
        # override to have anything to override. _get_validators() rejects
        # an unchanged blank pwd whenever repository.defaults.type is
        # SA_SQL, so a deployment that forgets to supply a credential fails
        # closed with a clear message instead of silently connecting with a
        # known password. Local dev/test supplies uid/pwd explicitly via
        # *_REPOSITORY__DEFAULTS__PROPS__UID/PWD env vars (see
        # docker-compose.sql*.yml and test/conftest.py); a real deployment
        # overrides them the same way, or via a secrets file.
        "repository": {
            "defaults": {
                "type": "SA_SQL",
                "props": {
                    "driver": "ODBC Driver 18 for SQL Server",
                    "server": "127.0.0.1",
                    "database": "commondb",
                    "uid": "",
                    "pwd": "",
                    "other": ";TrustServerCertificate=yes",
                    "connection_string": _SA_SQL_CONNECTION_STRING,
                },
            },
            # Deliberately no per-repo "props" here: _init_validate_settings's
            # shallow `repository.defaults | repository.<x>` merge takes the
            # whole `props` dict from whichever side has it, not a per-key
            # merge — a repo with no "props" key of its own falls through to
            # `repository.defaults.props` (the connection_string above)
            # entirely, and a repo whose props ARE overridden (a `file` path,
            # for the DICT/SA_SQLITE backends) replaces it entirely, rather
            # than the stale connection_string coexisting alongside `file`.
            "abac": {
                "module": "gen_epix.commondb.repositories",
                "class_name": "AbacSARepository",
            },
            "organization": {
                "module": "gen_epix.commondb.repositories",
                "class_name": "OrganizationSARepository",
            },
            "system": {
                "module": "gen_epix.commondb.repositories",
                "class_name": "SystemSARepository",
            },
        },
    }

    # The top-level tables this framework's configuration ever populates.
    # to_dict()/to_toml() filter Dynaconf's as_dict(internal=False) output
    # down to these keys, since as_dict(internal=False) does not scrub every
    # constructor keyword argument Dynaconf was given (an explicit
    # envvar_separator argument, for example, surfaces as an
    # ENVVAR_SEPARATOR key in its output).
    _EXPORTABLE_TOP_LEVEL_KEYS = (
        "app",
        "api",
        "log",
        "service",
        "repository",
        "feature_flags",
    )

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

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge `override` on top of `base`, returning a new dict.

        Values in `override` win on key collision. Only dict-vs-dict pairs
        recurse; any other type (list, scalar, or a dict overriding a
        non-dict) replaces the `base` value wholesale.

        Args:
            base: Lower-precedence dict (not mutated).
            override: Higher-precedence dict (not mutated).

        Returns:
            A new, merged dict; neither input is mutated.
        """
        merged = dict(base)
        for key, override_value in override.items():
            base_value = merged.get(key)
            if isinstance(base_value, dict) and isinstance(override_value, dict):
                merged[key] = AppCfg._deep_merge(base_value, override_value)
            else:
                merged[key] = override_value
        return merged

    def _get_default_settings(self) -> dict[str, Any]:
        """Return a fresh, mutation-safe copy of this class's business defaults.

        Subclasses only need to declare their own `_DEFAULT_SETTINGS` class
        attribute — `self._DEFAULT_SETTINGS` already resolves to the
        subclass's own attribute via normal MRO. The feature-flags section
        is assembled here, not in the `_DEFAULT_SETTINGS` literal, because
        gen_epix.commondb.domain.enum cannot be imported at module scope in
        this file: gen_epix.commondb.domain imports this configuration
        package back (through its own util module), so importing the enum
        module before AppCfg finishes being defined would deadlock the
        import graph. Importing it here, inside a method called from
        __init__, runs after both packages have finished loading.

        Returns:
            Deep copy of `type(self)._DEFAULT_SETTINGS`, with `feature_flags` added.
        """
        from gen_epix.commondb.domain.enum import (  # noqa: PLC0415
            FEATURE_FLAG_TOML_KEYS,
        )

        settings = copy.deepcopy(self._DEFAULT_SETTINGS)
        settings["feature_flags"] = {
            flag.value: False for flag in FEATURE_FLAG_TOML_KEYS
        }
        return settings

    def _get_feature_flag_validators(self) -> list[Validator]:
        """Build validators for this app's `[feature_flags]` table entries.

        Bool-like strings ("0", "1", "true", "false") are accepted, since
        envsubst-rendered TOML yields strings; AppComposer converts them.
        """
        from gen_epix.commondb.domain.enum import (  # noqa: PLC0415
            FEATURE_FLAG_TOML_KEYS,
        )

        return [
            Validator(
                f"feature_flags.{flag.value}",
                condition=lambda v: convert_to_bool(v)[0],
                messages={
                    "condition": (
                        "{name} must be a boolean or one of "
                        '"true", "false", "1", "0", but it is {value!r}.'
                    )
                },
            )
            for flag in FEATURE_FLAG_TOML_KEYS
        ]

    @staticmethod
    def _factory_names(factory_class: type) -> list[str]:
        """Return the class-body-defined factory names on a *Factory class.

        TimestampFactory/IdFactory assign a function (e.g. `uuid.uuid4`, a
        lambda) to each name rather than a plain value. Python's Enum
        machinery treats a callable assigned in a class body as a method,
        not a member, so these classes have no iterable members at all —
        `list(TimestampFactory)` is always empty, even though
        `getattr(TimestampFactory, "DATETIME_NOW")` (used by
        `_init_validate_settings`) resolves it correctly. This reads the
        same names directly from the class's own namespace instead.
        """
        return [
            name
            for name, value in vars(factory_class).items()
            if not name.startswith("_") and callable(value)
        ]

    def _get_validators(self) -> list[Validator]:
        """Build the Dynaconf validators for this instance's configuration shape.

        Combines validators that hold for every app (port/log-level types,
        the closed sets of factory names) with validators derived from this
        instance's own service/repository enums, so a bad settings file or
        environment variable is rejected with a specific message at load
        time rather than surfacing later as an unrelated AttributeError.
        """
        from gen_epix.commondb.domain.enum import (  # noqa: PLC0415
            IdFactory,
            TimestampFactory,
        )

        validators = [
            Validator("app.port", is_type_of=int),
            Validator("log.level", is_in=list(_STANDARD_LOG_LEVELS)),
            Validator(
                "service.defaults.props.timestamp_factory",
                is_in=self._factory_names(TimestampFactory),
            ),
            Validator(
                "service.defaults.props.id_factory",
                is_in=self._factory_names(IdFactory),
            ),
            Validator(
                "repository.defaults.type",
                is_in=[member.name for member in self._repository_type_enum],
            ),
            # SA_SQL's uid/pwd default to "" (see _DEFAULT_SETTINGS's
            # comment) so that an env var/settings-file override has an
            # existing key to override. Reject an unchanged blank pwd
            # whenever SA_SQL is the resolved repository type AND the
            # resolved connection_string still embeds that blank pwd (the
            # built-in default template), so a deployment that forgot to
            # supply a credential fails closed with a clear message instead
            # of silently connecting with an empty password. A deployment
            # that supplies its own complete connection_string (e.g. from a
            # secret store) needs no separate pwd and passes.
            Validator(
                "repository.defaults.props.pwd",
                condition=lambda v: v != "",
                when=Validator("repository.defaults.type", eq="SA_SQL")
                & Validator(
                    "repository.defaults.props.connection_string",
                    condition=lambda v: (
                        _BLANK_PWD_IN_CONNECTION_STRING.search(v) is not None
                    ),
                ),
                messages={
                    "condition": (
                        "SA_SQL repository requires a credential: set "
                        "{name} via a settings file or the "
                        "<APP>_REPOSITORY__DEFAULTS__PROPS__PWD environment "
                        "variable (and, usually, ...__UID alongside it), or "
                        "supply a complete "
                        "repository.defaults.props.connection_string."
                    )
                },
            ),
        ]
        for service_type in self._service_type_enum:
            service_type_str = service_type.value.lower()
            validators.append(
                Validator(
                    f"service.{service_type_str}.module",
                    f"service.{service_type_str}.class_name",
                    must_exist=True,
                    is_type_of=str,
                )
            )
        validators.extend(self._get_feature_flag_validators())
        return validators

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
        """Load settings using SettingsManager, seeded with this class's defaults."""
        settings_manager = SettingsManager(
            prefix=self._envvar_prefix, settings_files=self._settings_files
        )
        self._cfg = settings_manager.load_settings(
            defaults=self._get_default_settings(),
            validators=self._get_validators(),
        )
        # Captured before _init_validate_settings mutates self._cfg in place
        # (it injects a live class object per service/repository, and
        # resolves factory/enum-name strings into live objects) — this
        # snapshot is what to_toml()/to_dict() export, since none of that
        # is TOML-serializable or should round-trip.
        self._raw_cfg_snapshot: dict[str, Any] = self._cfg.as_dict(internal=False)
        # Explicit settings_files mode has no defaults to compare against.
        if not self._settings_files:
            self._warn_unrecognised_keys()

    # Dynaconf bookkeeping keys that surface at the top level of as_dict()
    # (lowercase for comparison); they are never business configuration.
    _DYNACONF_INTERNAL_KEYS = frozenset({"envvar_separator", "post_hooks"})

    # Path patterns (lowercase, dotted, fnmatch-style) that legitimately
    # hold keys absent from the defaults, because their content is
    # backend-specific or declared per deployment: repository props differ
    # per backend (`file`, `dir`, `variant`, ...), and a settings file adds
    # identity-provider entries.
    _OPEN_ENDED_KEY_PATHS = ("repository.*.props", "service.auth.props.idps_cfg")

    @classmethod
    def _find_unrecognised_keys(
        cls,
        loaded: dict[str, Any],
        defaults: dict[str, Any],
        _path: str = "",
    ) -> list[str]:
        """Return dotted paths in `loaded` that `defaults` has no key for.

        Every key a settings file or environment variable may override
        exists in the defaults as a placeholder (see _DEFAULT_SETTINGS), so
        a loaded key without a default is a typo or a setting this version
        does not read. Keys compare case-insensitively (Dynaconf's
        as_dict() upper-cases the top level); reported paths are lowercase.
        Recursion stops at a key missing from the defaults, and at
        _OPEN_ENDED_KEY_PATHS.
        """
        known = {str(key).lower(): key for key in defaults}
        unrecognised: list[str] = []
        for key, value in loaded.items():
            lowered = str(key).lower()
            path = f"{_path}.{lowered}" if _path else lowered
            if not _path and lowered in cls._DYNACONF_INTERNAL_KEYS:
                continue
            if any(fnmatchcase(path, pat) for pat in cls._OPEN_ENDED_KEY_PATHS):
                continue
            if lowered not in known:
                unrecognised.append(path)
            elif isinstance(value, dict) and isinstance(defaults[known[lowered]], dict):
                unrecognised.extend(
                    cls._find_unrecognised_keys(value, defaults[known[lowered]], path)
                )
        return unrecognised

    def _warn_unrecognised_keys(self) -> None:
        """Warn about loaded settings keys that this app's defaults do not know.

        A warning rather than an error, because an overlay may legitimately
        carry keys meant for a newer version of this package. Typos are
        otherwise silent: the intended setting just keeps its default.
        """
        unrecognised = self._find_unrecognised_keys(
            self._raw_cfg_snapshot, self._get_default_settings()
        )
        if unrecognised and self._log_setup:
            self.setup_logger.warning(
                App.create_static_log_message(
                    "5be0d7a2",
                    f"Ignoring unrecognised settings keys for app "
                    f"{self._app_name!r} (typo, or not read by this version): "
                    f"{', '.join(sorted(unrecognised))}",
                )
            )

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
            try:
                service_cfg["class"] = getattr(
                    importlib.import_module(service_module), service_class_name
                )
            except (ImportError, AttributeError) as error:
                raise exc.InitializationServiceError(
                    "a8811d58",
                    f"Cannot resolve service.{service_type_str} for app "
                    f"{self._app_name!r}: module={service_module!r}, "
                    f"class_name={service_class_name!r}",
                ) from error
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
            try:
                repository_cfg["class"] = getattr(
                    importlib.import_module(repository_module), repository_class_name
                )
            except (ImportError, AttributeError) as error:
                raise exc.RepositoryInitializationServiceError(
                    "c07ef709",
                    f"Cannot resolve repository.{service_type_str} for app "
                    f"{self._app_name!r}: module={repository_module!r}, "
                    f"class_name={repository_class_name!r}",
                ) from error
            self._cfg["repository"][service_type_str] = repository_cfg

    @property
    def cfg(self) -> cfg_types.ResolvedAppCfgSettingsDict:
        """Loaded, validated Dynaconf settings object.

        The returned value is still the live Dynaconf Box; this narrows its
        static type from Dynaconf (effectively Any under this repo's mypy
        configuration, since dynaconf ships no type information) to the
        resolved settings shape, without converting the runtime object.
        """
        return cast(cfg_types.ResolvedAppCfgSettingsDict, self._cfg)

    # Extra key names (beyond json_logging's own defaults) redacted when
    # to_dict()/to_toml() are called with redact=True — the config-specific
    # field names that carry a repository credential, plus the assembled
    # connection string, whose embedded "PWD=..."/"UID=..." fragments
    # redact_nested's pattern-based pass also catches wherever they appear.
    _EXPORT_SENSITIVE_KEYS = ("uid", "pwd")

    def to_dict(self, resolved: bool = False, redact: bool = False) -> dict[str, Any]:
        """Return this config as a plain, TOML-serializable dict.

        Args:
            resolved: If False (default), returns the round-trippable
                pre-validation snapshot (defaults, settings files, and
                environment variables merged, nothing resolved to a live
                Python object) — this is what `to_toml()` writes, and can be
                fed back in as a settings file. If True, returns a
                display-only copy of the post-validation config with
                non-serializable values (factory objects, enum members,
                imported classes) stringified — not meant to be reloaded.
            redact: If True, replace credential-shaped values (repository
                uid/pwd, and any "pwd=..."/"uid=..." fragment embedded in a
                connection string) with a redaction placeholder. Default
                False keeps output round-trippable as documented above;
                pass True for a copy that's safe to paste into a ticket,
                log, or chat.

        Returns:
            Filtered dict containing only known top-level config sections.
        """
        source = self._cfg if resolved else self._raw_cfg_snapshot
        raw = {
            k.lower(): v
            for k, v in dict(source).items()
            if k.lower() in self._EXPORTABLE_TOP_LEVEL_KEYS
        }
        if not resolved:
            result = copy.deepcopy(raw)
        else:
            result = cast(
                dict[str, Any], AppCfg._stringify_non_serializable(copy.deepcopy(raw))
            )
        if redact:
            from gen_epix.commondb.config.json_logging import (  # noqa: PLC0415
                redact_nested,
            )

            result = redact_nested(result, self._EXPORT_SENSITIVE_KEYS)
        return result

    @staticmethod
    def _stringify_non_serializable(value: Any) -> Any:
        """Recursively replace non-TOML-serializable values with their repr()."""
        if isinstance(value, dict):
            return {k: AppCfg._stringify_non_serializable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [AppCfg._stringify_non_serializable(v) for v in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return repr(value)

    def to_toml(
        self,
        path: Path | str | None = None,
        resolved: bool = False,
        redact: bool = False,
    ) -> str:
        """Serialize this config to a TOML string, optionally writing it to disk.

        Args:
            path: If given, also write the TOML text to this path.
            resolved: See `to_dict`.
            redact: See `to_dict`.

        Returns:
            The TOML text.
        """
        import tomli_w  # noqa: PLC0415  # local import: keeps tomli_w off AppCfg's hot import path

        text = tomli_w.dumps(self.to_dict(resolved=resolved, redact=redact))
        if path is not None:
            Path(path).write_text(text, encoding=getpreferredencoding())
        return text

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
        # Mirror into the pre-validation export snapshot too, so
        # to_dict(resolved=False)/to_toml() reflect the same <APP>_LOG_LEVEL
        # override applied to the live config above, instead of always
        # showing the settings-file value from before this override ran.
        if hasattr(self, "_raw_cfg_snapshot") and "log" in self._raw_cfg_snapshot:
            self._raw_cfg_snapshot["log"]["level"] = resolved_level
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


assert set(AppCfg._EXPORTABLE_TOP_LEVEL_KEYS) == (
    cfg_types.AppCfgSettingsDict.__required_keys__
    | cfg_types.AppCfgSettingsDict.__optional_keys__
)
