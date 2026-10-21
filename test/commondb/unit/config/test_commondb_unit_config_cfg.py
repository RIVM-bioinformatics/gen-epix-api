import importlib
import json
import logging
import os
import tempfile
import textwrap
import tomllib
from pathlib import Path
from typing import Any, Iterator, cast

import pytest
from dynaconf.validator import ValidationError

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import (
    AppType,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.domain.enum import FeatureFlag as CommonFeatureFlag
from gen_epix.commondb.domain.enum import RepositoryType, ServiceType
from gen_epix.commondb.domain.service import BaseAuthService
from gen_epix.commondb.domain.util import get_app_cfg_class, set_env_variables
from gen_epix.commondb.env import AppComposer
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import FeatureFlag as FastappFeatureFlag

_REPO_ROOT = Path(__file__).parents[4]
_APP_IMPORT_SPECS = {
    app_name: {"default_auto_create_new_users": False}
    for app_name in ("CASEDB", "COMMONDB", "SEQDB", "OMOPDB")
}
_TEST_CFG_DIR = _REPO_ROOT / "gen_epix" / "commondb" / "config" / "test"
_TEST_CFG_FILES = {
    "EMPTY_DB_DICT": [_TEST_CFG_DIR / "empty_db_dict.toml"],
    "EMPTY_DB_SQLITE_INMEM": [_TEST_CFG_DIR / "empty_db_sqlite_inmem.toml"],
}


def _read_config(
    app_name: str,
    extra_settings_files: list[Path] | None = None,
    settings_files: list[Path] | None = None,
) -> dict:
    """Construct and compose an app config, returning key config/auth values."""
    if settings_files is None:
        set_env_variables(
            AppType[app_name],
            DevIdpConfig.NONE,
            DevRepositoryConfig.DICT_EMPTY,
            extra_settings_files=extra_settings_files,
        )
    for log_app in AppType:
        os.environ[f"{log_app.name}_LOG_LEVEL"] = "WARNING"

    enum_module = importlib.import_module(f"gen_epix.{app_name.lower()}.domain.enum")
    app_composer_module = importlib.import_module(f"gen_epix.{app_name.lower()}.env")
    app_cfg = get_app_cfg_class(app_name)(
        app_name,
        enum_module.ServiceType,
        enum_module.RepositoryType,
        settings_files=(
            [str(path.resolve()) for path in settings_files] if settings_files else None
        ),
        log_any=False,
    )
    app_composer: AppComposer = app_composer_module.AppComposer(app_cfg)

    app = app_composer.app
    auth_service: BaseAuthService = app_composer.services[  # type: ignore[assignment]
        enum_module.ServiceType.AUTH
    ]
    cfg = cast(dict[str, Any], app_cfg.cfg)
    auth_props = cast(dict[str, Any], cfg["service"]["auth"]["props"])
    auth_service_any = cast(Any, auth_service)

    return {
        "app_cfg_type": type(app_cfg).__name__,
        "app_composer_type": type(app_composer).__name__,
        "cfg_auto_create_new_users": auth_props["auto_create_new_users"],
        "cfg_root_token_time_to_live": auth_props["root_token_time_to_live"],
        "feature_flag_auto_create_new_users": app.get_feature_flag(
            FastappFeatureFlag.AUTO_CREATE_NEW_USERS
        ),
        "feature_flag_update_own_organization": app.get_feature_flag(
            CommonFeatureFlag.UPDATE_OWN_ORGANIZATION
        ),
        "service_root_token_time_to_live": auth_service_any._root_token_time_to_live,
        "service_idp_client_count": len(auth_service_any.idp_clients),
    }


@pytest.fixture
def override_tmp_dir() -> Iterator[Path]:
    parent_dir = _REPO_ROOT / "test" / "output" / __name__
    parent_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent_dir) as tmp_dir:
        yield Path(tmp_dir)


def _write_string_auth_override_file(override_tmp_dir: Path, app_name: str) -> Path:
    override_path = override_tmp_dir / f"{app_name.lower()}.toml"
    override_path.write_text(
        textwrap.dedent("""\
            [service.auth.props]
            auto_create_new_users = "0"
            root_token_time_to_live = "900"
            """),
        encoding="utf-8",
    )
    return override_path


def _assert_default_import_payload(payload: dict, app_name: str) -> None:
    spec = _APP_IMPORT_SPECS[app_name]
    assert payload["app_cfg_type"] == get_app_cfg_class(app_name).__name__
    assert payload["app_composer_type"] == "AppComposer"
    assert payload["cfg_auto_create_new_users"] is spec["default_auto_create_new_users"]
    assert payload["cfg_root_token_time_to_live"] == 0
    assert (
        payload["feature_flag_auto_create_new_users"]
        is spec["default_auto_create_new_users"]
    )
    assert payload["feature_flag_update_own_organization"] is False
    assert (
        payload["service_root_token_time_to_live"]
        == payload["cfg_root_token_time_to_live"]
    )
    assert payload["service_idp_client_count"] == 0


def _assert_string_override_payload(payload: dict, app_name: str) -> None:
    assert payload["app_cfg_type"] == get_app_cfg_class(app_name).__name__
    assert payload["app_composer_type"] == "AppComposer"
    assert payload["cfg_auto_create_new_users"] is False
    assert payload["cfg_root_token_time_to_live"] == 900
    assert payload["feature_flag_auto_create_new_users"] is False
    assert payload["feature_flag_update_own_organization"] is False
    assert payload["service_root_token_time_to_live"] == 900
    assert payload["service_idp_client_count"] == 0


def _write_override_file(override_tmp_dir: Path, name: str, content: str) -> Path:
    override_path = override_tmp_dir / name
    override_path.write_text(textwrap.dedent(content), encoding="utf-8")
    return override_path


_EXPORTABLE_TOP_LEVEL_KEYS = (
    "app",
    "api",
    "log",
    "service",
    "repository",
    "feature_flags",
)


def _build_app_cfg() -> AppCfg:
    set_env_variables(
        AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.DICT_EMPTY
    )
    os.environ["COMMONDB_LOG_LEVEL"] = "WARNING"
    return AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)


class _DummyHandler:
    def __init__(self, level: int = logging.INFO) -> None:
        self.level = level

    def setLevel(self, level: int | str) -> None:
        self.level = level


class _DummyLogger:
    def __init__(self, name: str, handlers: list[_DummyHandler] | None = None) -> None:
        self.name = name
        self.level: int | str | None = None
        self.handlers: list[_DummyHandler] = handlers or [_DummyHandler()]
        self.messages: list[tuple[str, str]] = []

    def setLevel(self, level: int | str) -> None:
        self.level = level

    def debug(self, msg: str) -> None:
        self.messages.append(("DEBUG", msg))

    def info(self, msg: str) -> None:
        self.messages.append(("INFO", msg))


def _build_test_fixture(
    *, shared_handler: bool, log_setup: bool
) -> tuple[AppCfg, dict[str, _DummyLogger], _DummyHandler]:
    """Create an AppCfg test instance with controllable dummy loggers and handlers."""
    app_cfg = AppCfg.__new__(AppCfg)
    app_cfg._log_any = True
    app_cfg._envvar_prefix = "CASEDB_"
    app_cfg._logger_prefix = "casedb"
    app_cfg._log_level_envvar = "LOG_LEVEL"
    app_cfg._log_setup = log_setup
    app_cfg._cfg = {"log": {"level": "INFO"}}
    app_cfg._logging_config_yaml = {
        "loggers": {
            "casedb.setup": {"level": "INFO"},
            "casedb.service": {"level": "INFO"},
            "casedb.app": {"level": "INFO"},
            "casedb.api": {"level": "INFO"},
            "casedb.external": {"level": "INFO"},
            "sqlalchemy.engine": {"level": "WARNING"},
            "sqlalchemy.pool": {"level": "WARNING"},
            "httpx": {"level": "INFO"},
            "asyncio": {"level": "WARNING"},
            "uvicorn.error": {"level": "INFO"},
        }
    }
    handler = _DummyHandler()
    logger_map: dict[str, _DummyLogger] = {}
    for logger_name in app_cfg._logging_config_yaml["loggers"]:
        handlers = [handler] if shared_handler else [_DummyHandler()]
        logger_map[logger_name] = _DummyLogger(logger_name, handlers=handlers)

    app_cfg._setup_logger = logger_map["casedb.setup"]
    app_cfg._service_logger = logger_map["casedb.service"]
    app_cfg._app_logger = logger_map["casedb.app"]
    app_cfg._api_logger = logger_map["casedb.api"]

    return app_cfg, logger_map, handler


def _patch_logging_get_logger(
    monkeypatch: pytest.MonkeyPatch, logger_map: dict[str, _DummyLogger]
) -> None:
    """Patch logging.getLogger so tests can inspect logger state deterministically."""
    original_get_logger = logging.getLogger

    def _get_logger(name: str | None = None):  # type: ignore[no-untyped-def]
        if name is None:
            return original_get_logger()
        return logger_map[name]

    monkeypatch.setattr(logging, "getLogger", _get_logger)


def _patch_runtime_logger_dict(
    monkeypatch: pytest.MonkeyPatch, names: list[str] | None = None
) -> None:
    """Patch runtime logger registry with synthetic logger names for descendant tests."""
    logger_names = names or []
    monkeypatch.setattr(
        logging.root.manager,
        "loggerDict",
        {name: object() for name in logger_names},
    )


def _extract_diagnostic_payload(logger: _DummyLogger) -> dict:
    """Return the latest APPLIED_LOG_LEVEL diagnostic payload from a dummy logger."""
    for level, msg in reversed(logger.messages):
        if level != "INFO":
            continue
        payload = json.loads(msg)
        if payload.get("msg") == "APPLIED_LOG_LEVEL":
            return payload
    raise AssertionError("Missing APPLIED_LOG_LEVEL diagnostic payload")


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_mirrors_override_into_raw_cfg_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """to_dict(resolved=False)/to_toml() read _raw_cfg_snapshot, captured once in

    _init_load_settings before set_log_level's <APP>_LOG_LEVEL override is
    applied to the live _cfg — set_log_level must mirror that override into
    the snapshot too, or the pre-validation export silently disagrees with
    the live config's actual log level."""
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=False)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    app_cfg._raw_cfg_snapshot = {"log": {"level": "INFO"}}
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level()

    assert app_cfg._cfg["log"]["level"] == "WARNING"
    assert app_cfg._raw_cfg_snapshot["log"]["level"] == "WARNING"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_without_raw_cfg_snapshot_does_not_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The first set_log_level call in __init__ runs before _raw_cfg_snapshot

    exists at all; set_log_level must tolerate that, not assume it's set."""
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=False)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    assert not hasattr(app_cfg, "_raw_cfg_snapshot")

    app_cfg.set_log_level("DEBUG")  # must not raise

    assert app_cfg._cfg["log"]["level"] == "DEBUG"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_preserves_pinned_third_party_loggers_without_handler_overwrite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_cfg, logger_map, shared_handler = _build_test_fixture(
        shared_handler=True, log_setup=False
    )
    logger_map["sqlalchemy.engine.Engine"] = _DummyLogger("sqlalchemy.engine.Engine")
    logger_map["sqlalchemy.pool.impl.QueuePool"] = _DummyLogger(
        "sqlalchemy.pool.impl.QueuePool"
    )
    _patch_logging_get_logger(monkeypatch, logger_map)
    monkeypatch.setattr(
        logging.root.manager,
        "loggerDict",
        {
            "sqlalchemy.engine.Engine": object(),
            "sqlalchemy.pool.impl.QueuePool": object(),
        },
    )

    app_cfg.set_log_level("DEBUG")

    assert app_cfg._cfg["log"]["level"] == "DEBUG"
    assert shared_handler.level == logging.NOTSET
    assert logger_map["casedb.setup"].level == "INFO"
    assert logger_map["casedb.service"].level == "INFO"
    assert logger_map["casedb.app"].level == "INFO"
    assert logger_map["casedb.api"].level == "INFO"
    assert logger_map["casedb.external"].level == "INFO"
    assert logger_map["sqlalchemy.engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool"].level == "WARNING"
    assert logger_map["sqlalchemy.engine.Engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool.impl.QueuePool"].level == "WARNING"
    assert logger_map["httpx"].level == "INFO"
    assert logger_map["asyncio"].level == "WARNING"
    assert logger_map["uvicorn.error"].level == "DEBUG"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_diagnostic_precedence_arg_over_env_and_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level("ERROR")

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "ERROR"
    assert diagnostic["resolved_level"] == "ERROR"
    assert diagnostic["source"] == "arg"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] == "WARNING"
    assert diagnostic["settings_value"] == "INFO"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_diagnostic_precedence_env_over_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level()

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "WARNING"
    assert diagnostic["resolved_level"] == "WARNING"
    assert diagnostic["source"] == "env"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] == "WARNING"
    assert diagnostic["settings_value"] == "INFO"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_diagnostic_precedence_settings_when_env_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.delenv("CASEDB_LOG_LEVEL", raising=False)

    app_cfg.set_log_level()

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "INFO"
    assert diagnostic["resolved_level"] == "INFO"
    assert diagnostic["source"] == "settings"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] is None
    assert diagnostic["settings_value"] == "INFO"


def test_to_dict_unresolved_contains_known_top_level_keys() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    assert set(payload.keys()) == set(_EXPORTABLE_TOP_LEVEL_KEYS)
    assert payload["app"]["port"] == 8010
    assert payload["repository"]["defaults"]["type"] == "DICT"


def test_to_dict_unresolved_values_are_plain_strings_not_resolved_objects() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    auth_entry = cast(dict[str, Any], payload["service"]["auth"])
    assert isinstance(auth_entry["module"], str)
    assert "class" not in auth_entry


def test_to_dict_resolved_stringifies_non_serializable_values() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=True)

    auth_entry = cast(dict[str, Any], payload["service"]["auth"])
    assert isinstance(auth_entry["class"], str)
    assert "AuthService" in auth_entry["class"]


def test_to_toml_round_trips_via_tomllib(tmp_path: Path) -> None:
    app_cfg = _build_app_cfg()
    out_path = tmp_path / "exported.toml"

    text = app_cfg.to_toml(path=out_path, resolved=False)

    assert out_path.is_file()
    written = tomllib.loads(out_path.read_text(encoding="utf-8"))
    parsed = tomllib.loads(text)
    assert written == parsed
    assert parsed["app"]["port"] == 8010


def test_to_toml_without_path_returns_text_only() -> None:
    app_cfg = _build_app_cfg()

    text = app_cfg.to_toml()

    assert tomllib.loads(text)["app"]["port"] == 8010


@pytest.mark.parametrize("resolved", [True, False])
def test_to_dict_filters_to_known_keys_only(resolved: bool) -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=resolved)

    assert set(payload.keys()) <= set(_EXPORTABLE_TOP_LEVEL_KEYS)


def test_to_dict_default_does_not_redact_credentials() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    props = payload["repository"]["defaults"]["props"]
    assert props["uid"] == "sa"
    assert props["pwd"] == "Your_password123"
    assert "Your_password123" in props["connection_string"]


def test_to_dict_redact_true_scrubs_credentials() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False, redact=True)

    props = payload["repository"]["defaults"]["props"]
    assert props["uid"] == "[REDACTED]"
    assert props["pwd"] == "[REDACTED]"
    assert "Your_password123" not in props["connection_string"]
    assert props["driver"] == "ODBC Driver 18 for SQL Server"


def test_to_toml_redact_true_scrubs_credentials() -> None:
    app_cfg = _build_app_cfg()

    text = app_cfg.to_toml(redact=True)

    assert "Your_password123" not in text
    assert '"[REDACTED]"' in text or "'[REDACTED]'" in text


def test_to_dict_top_level_keys_match_source_file_casing() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    assert all(key == key.lower() for key in payload)


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_casedb_read_config_defaults() -> None:
    _assert_default_import_payload(_read_config("CASEDB"), "CASEDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
@pytest.mark.parametrize(
    "settings_file_key", ["EMPTY_DB_DICT", "EMPTY_DB_SQLITE_INMEM"]
)
def test_commondb_read_config_with_constructor_settings_files(
    settings_file_key: str,
) -> None:
    payload = _read_config(
        "COMMONDB", settings_files=_TEST_CFG_FILES[settings_file_key]
    )
    _assert_default_import_payload(payload, "COMMONDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_casedb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "CASEDB")
    _assert_string_override_payload(
        _read_config("CASEDB", extra_settings_files=[override_file]), "CASEDB"
    )


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_seqdb_read_config_defaults() -> None:
    _assert_default_import_payload(_read_config("SEQDB"), "SEQDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_seqdb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "SEQDB")
    _assert_string_override_payload(
        _read_config("SEQDB", extra_settings_files=[override_file]), "SEQDB"
    )


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_omopdb_read_config_defaults() -> None:
    _assert_default_import_payload(_read_config("OMOPDB"), "OMOPDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_omopdb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "OMOPDB")
    _assert_string_override_payload(
        _read_config("OMOPDB", extra_settings_files=[override_file]), "OMOPDB"
    )


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_read_config_rejects_unknown_id_factory(override_tmp_dir: Path) -> None:
    override_file = _write_override_file(
        override_tmp_dir,
        "bad_id_factory.toml",
        """\
        [service.defaults.props]
        id_factory = "NOT_A_FACTORY"
        """,
    )
    with pytest.raises(ValidationError):
        _read_config("CASEDB", extra_settings_files=[override_file])


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_read_config_rejects_unresolvable_service_module(
    override_tmp_dir: Path,
) -> None:
    override_file = _write_override_file(
        override_tmp_dir,
        "bad_service_module.toml",
        """\
        [service.case]
        module = "gen_epix.nonexistent_module_path"
        class_name = "CaseService"
        """,
    )
    with pytest.raises(exc.InitializationServiceError):
        _read_config("CASEDB", extra_settings_files=[override_file])


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_read_config_rejects_unknown_repository_type(override_tmp_dir: Path) -> None:
    override_file = _write_override_file(
        override_tmp_dir,
        "bad_repository_type.toml",
        """\
        [repository.defaults]
        type = "NOT_A_TYPE"
        """,
    )
    with pytest.raises(ValidationError):
        _read_config("CASEDB", extra_settings_files=[override_file])


def test_sa_sql_without_credentials_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", raising=False)
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", raising=False)
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)
    with pytest.raises(ValidationError):
        AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)


def test_sa_sql_with_credential_env_vars_constructs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", "sa")
    monkeypatch.setenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", "Your_password123")
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)
    app_cfg = AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)
    assert app_cfg.cfg["repository"]["defaults"]["props"]["uid"] == "sa"


def test_sa_sql_with_complete_connection_string_constructs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", raising=False)
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", raising=False)
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)
    monkeypatch.setenv(
        "COMMONDB_REPOSITORY__DEFAULTS__PROPS__CONNECTION_STRING",
        "mssql+pyodbc:///?odbc_connect=DRIVER=X;SERVER=s;DATABASE=d;UID=u;PWD=from-key-vault",
    )
    app_cfg = AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)
    assert app_cfg.cfg["repository"]["defaults"]["props"]["pwd"] == ""


def test_sa_sql_connection_string_with_blank_pwd_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", raising=False)
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", raising=False)
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)
    monkeypatch.setenv(
        "COMMONDB_REPOSITORY__DEFAULTS__PROPS__CONNECTION_STRING",
        "mssql+pyodbc:///?odbc_connect=DRIVER=X;SERVER=s;DATABASE=d;UID=u;PWD=;",
    )
    with pytest.raises(ValidationError):
        AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_read_config_rejects_non_bool_feature_flag(override_tmp_dir: Path) -> None:
    override_file = _write_override_file(
        override_tmp_dir,
        "bad_feature_flag.toml",
        """\
        [feature_flags]
        update_own_organization = "yes"
        """,
    )
    with pytest.raises(ValidationError):
        _read_config("CASEDB", extra_settings_files=[override_file])


@pytest.mark.scenario_ids("TC-CFG-01-01")
@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [("0", False), ("1", True), ("false", False), ("TRUE", True)],
)
def test_read_config_accepts_bool_like_string_feature_flag(
    override_tmp_dir: Path, raw_value: str, expected: bool
) -> None:
    override_file = _write_override_file(
        override_tmp_dir,
        "bool_like_feature_flag.toml",
        f"""\
        [feature_flags]
        update_own_organization = "{raw_value}"
        """,
    )
    payload = _read_config("CASEDB", extra_settings_files=[override_file])
    assert payload["feature_flag_update_own_organization"] is expected


def _capture_setup_warnings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    from gen_epix.commondb.config import cfg as cfg_module

    messages: list[str] = []
    monkeypatch.setattr(
        cfg_module._NULL_LOGGER,
        "warning",
        lambda msg, *args, **kwargs: (
            messages.append(str(msg)) if '"5be0d7a2"' in str(msg) else None
        ),
    )
    return messages


def test_unrecognised_settings_key_warns(
    override_tmp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    messages = _capture_setup_warnings(monkeypatch)
    override_file = _write_override_file(
        override_tmp_dir,
        "typo.toml",
        """\
        [service.auth.props]
        root_token_time_to_liv = 5

        [app]
        prot = 1234
        """,
    )
    _read_config("CASEDB", extra_settings_files=[override_file])
    assert len(messages) == 1
    assert "service.auth.props.root_token_time_to_liv" in messages[0]
    assert "app.prot" in messages[0]


def test_valid_overlay_does_not_warn(
    override_tmp_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    messages = _capture_setup_warnings(monkeypatch)
    override_file = _write_override_file(
        override_tmp_dir,
        "valid.toml",
        """\
        [app]
        port = 1234

        [feature_flags]
        update_own_organization = true

        [api]
        default_route = "/docs"
        """,
    )
    _read_config("CASEDB", extra_settings_files=[override_file])
    assert messages == []


@pytest.mark.parametrize("app_name", ["CASEDB", "SEQDB", "OMOPDB", "COMMONDB"])
def test_default_configuration_does_not_warn(
    app_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    messages = _capture_setup_warnings(monkeypatch)
    _read_config(app_name)
    assert messages == []


def test_find_unrecognised_keys_helper() -> None:
    defaults = {"app": {"port": 1}, "service": {"auth": {"props": {"a": 1}}}}
    loaded = {
        "APP": {"port": 2, "prot": 3},
        "SERVICE": {
            "auth": {"props": {"a": 1, "idps_cfg": [{"name": "x"}], "b": {"c": 1}}}
        },
        "POST_HOOKS": [],
        "sevice": {"x": 1},
    }
    assert sorted(AppCfg._find_unrecognised_keys(loaded, defaults)) == [
        "app.prot",
        "service.auth.props.b",
        "sevice",
    ]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_set_log_level_env_override_updates_uvicorn_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level()

    assert logger_map["uvicorn.error"].level == "WARNING"
    assert logger_map["casedb.setup"].level == "INFO"
