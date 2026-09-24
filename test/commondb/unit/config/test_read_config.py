from __future__ import annotations

import importlib
import os
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Iterator, cast

import pytest

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.domain.service import BaseAuthService
from gen_epix.commondb.domain.util import set_env_variables
from gen_epix.commondb.env import AppComposer

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
    app_cfg = AppCfg(
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
            "auto_create_new_users"
        ),
        "feature_flag_update_own_organization": app.get_feature_flag(
            "update_own_organization"
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

    assert payload["app_cfg_type"] == "AppCfg"
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
    assert payload["app_cfg_type"] == "AppCfg"
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
