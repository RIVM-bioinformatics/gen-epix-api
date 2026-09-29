from __future__ import annotations

import importlib
import os
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Iterator, cast

import pytest
from dynaconf.validator import ValidationError

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import (
    AppType,
    DevIdpConfig,
    DevRepositoryConfig,
    FeatureFlag,
    RepositoryType,
    ServiceType,
)
from gen_epix.commondb.domain.service import BaseAuthService
from gen_epix.commondb.domain.util import get_app_cfg_class, set_env_variables
from gen_epix.commondb.env import AppComposer
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthFeatureFlag

_REPO_ROOT = Path(__file__).parents[4]
_APP_IMPORT_SPECS = {
    "CASEDB": {
        "default_auto_create_new_users": False,
    },
    "COMMONDB": {
        "default_auto_create_new_users": False,
    },
    "SEQDB": {
        "default_auto_create_new_users": False,
    },
    "OMOPDB": {
        "default_auto_create_new_users": False,
    },
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

    # Set environment variables
    if settings_files is None:
        set_env_variables(
            AppType[app_name],
            DevIdpConfig.NONE,
            DevRepositoryConfig.DICT_EMPTY,
            extra_settings_files=extra_settings_files,
        )
    for log_app in AppType:
        os.environ[f"{log_app.name}_LOG_LEVEL"] = "WARNING"

    # Construct AppCfg and AppComposer to trigger config loading and service initialization
    enum_module = importlib.import_module(f"gen_epix.{app_name.lower()}.domain.enum")
    app_composer_module = importlib.import_module(f"gen_epix.{app_name.lower()}.env")
    app_cfg = get_app_cfg_class(app_name)(
        app_name,
        enum_module.ServiceType,
        enum_module.RepositoryType,
        settings_files=(
            [str(x.resolve()) for x in settings_files] if settings_files else None
        ),
        log_any=False,
    )
    app_composer: AppComposer = app_composer_module.AppComposer(app_cfg)

    # Get some additional data from the auth service
    app = app_composer.app
    auth_service: BaseAuthService = app_composer.services[enum_module.ServiceType.AUTH]  # type: ignore[assignment]
    cfg = cast(dict[str, Any], app_cfg.cfg)
    auth_props = cast(dict[str, Any], cfg["service"]["auth"]["props"])
    auth_service_any = cast(Any, auth_service)

    retval = {
        "app_cfg_type": type(app_cfg).__name__,
        "app_composer_type": type(app_composer).__name__,
        "cfg_auto_create_new_users": auth_props["auto_create_new_users"],
        "cfg_root_token_time_to_live": auth_props["root_token_time_to_live"],
        "feature_flag_auto_create_new_users": app.get_feature_flag(
            AuthFeatureFlag.AUTO_CREATE_NEW_USERS
        ),
        "feature_flag_update_own_organization": app.get_feature_flag(
            FeatureFlag.UPDATE_OWN_ORGANIZATION
        ),
        "service_root_token_time_to_live": auth_service_any._root_token_time_to_live,
        "service_idp_client_count": len(auth_service_any.idp_clients),
    }
    return retval


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
    assert payload["cfg_auto_create_new_users"] == False
    assert payload["cfg_root_token_time_to_live"] == 900
    assert payload["feature_flag_auto_create_new_users"] is False
    assert payload["feature_flag_update_own_organization"] is False
    assert payload["service_root_token_time_to_live"] == 900
    assert payload["service_idp_client_count"] == 0


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_casedb_read_config_defaults() -> None:
    payload = _read_config("CASEDB")

    _assert_default_import_payload(payload, "CASEDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
@pytest.mark.parametrize(
    "settings_file_key",
    ["EMPTY_DB_DICT", "EMPTY_DB_SQLITE_INMEM"],
)
def test_commondb_read_config_with_constructor_settings_files(
    settings_file_key: str,
) -> None:
    payload = _read_config(
        "COMMONDB",
        settings_files=_TEST_CFG_FILES[settings_file_key],
    )

    _assert_default_import_payload(payload, "COMMONDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_casedb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "CASEDB")

    payload = _read_config("CASEDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "CASEDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_seqdb_read_config_defaults() -> None:
    payload = _read_config("SEQDB")

    _assert_default_import_payload(payload, "SEQDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_seqdb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "SEQDB")

    payload = _read_config("SEQDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "SEQDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_omopdb_read_config_defaults() -> None:
    payload = _read_config("OMOPDB")

    _assert_default_import_payload(payload, "OMOPDB")


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_omopdb_read_config_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "OMOPDB")

    payload = _read_config("OMOPDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "OMOPDB")


def _write_override_file(override_tmp_dir: Path, name: str, content: str) -> Path:
    override_path = override_tmp_dir / name
    override_path.write_text(textwrap.dedent(content), encoding="utf-8")
    return override_path


@pytest.mark.scenario_ids("TC-CFG-01-01")
def test_read_config_rejects_unknown_id_factory(override_tmp_dir: Path) -> None:
    """A settings file naming an id_factory outside the IdFactory enum fails validation."""
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
    """A settings file naming a service module that cannot be imported fails to resolve, not silently."""
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
    """A settings file naming a repository type outside the app's RepositoryType enum fails validation."""
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


def test_feature_flag_has_no_auto_create_new_users_member() -> None:
    """Regression guard: FeatureFlag must not redefine AuthFeatureFlag.AUTO_CREATE_NEW_USERS.

    A same-named-but-distinct Enum member here would collide in value but
    not identity with AuthFeatureFlag.AUTO_CREATE_NEW_USERS, the actual key
    App._feature_flags is set under — a caller querying the FeatureFlag
    version would silently see the default (False) regardless of the real
    configured value. See FeatureFlag's docstring.
    """
    assert "AUTO_CREATE_NEW_USERS" not in FeatureFlag.__members__


def test_sa_sql_without_credentials_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SA_SQL's repository defaults carry a blank pwd; construction must fail
    immediately (not silently connect with a known password) when neither a
    settings file nor an environment variable supplies a real credential."""
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", raising=False)
    monkeypatch.delenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", raising=False)
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)

    with pytest.raises(ValidationError):
        AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)


def test_sa_sql_with_credential_env_vars_constructs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Supplying the credential via the standard env var override (as
    docker-compose.sql*.yml and test/conftest.py both do) is enough."""
    monkeypatch.setenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__UID", "sa")
    monkeypatch.setenv("COMMONDB_REPOSITORY__DEFAULTS__PROPS__PWD", "Your_password123")
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.SA_SQL)

    app_cfg = AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)

    assert app_cfg.cfg["repository"]["defaults"]["props"]["uid"] == "sa"


def test_sa_sql_with_complete_connection_string_constructs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A deployment supplying its own complete connection_string (e.g. from
    Key Vault) needs no separate pwd."""
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
    """An overridden connection_string that itself embeds a blank PWD is still rejected."""
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
    """A settings file setting a feature flag to a non-bool value fails validation."""
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
    """Bool-like strings, as rendered by envsubst in lsp-api, resolve to real bools."""
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
    """Record unrecognised-key warnings sent to the null logger log_any=False installs."""
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
    """A typo'd key in an overlay is reported, naming the dotted path."""
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
    """Overriding known keys is not reported (backend-specific repository props are covered by the defaults test)."""
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
    """The shipped defaults plus the dev repository files trigger no warning."""
    messages = _capture_setup_warnings(monkeypatch)

    _read_config(app_name)

    assert messages == []


def test_find_unrecognised_keys_helper() -> None:
    """Case-insensitive, stops at unknown keys, skips open-ended paths and internals."""
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
