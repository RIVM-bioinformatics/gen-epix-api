"""Test AppCfg.to_dict()/to_toml() export."""

import os
import tomllib
from pathlib import Path
from typing import Any, cast

import pytest

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import (
    AppType,
    DevIdpConfig,
    DevRepositoryConfig,
    RepositoryType,
    ServiceType,
)
from gen_epix.commondb.domain.util import set_env_variables

# Dynaconf's internal dict() casting always uppercases top-level Settings
# keys, regardless of lowercase_read or the source file's own casing;
# nested keys retain whatever casing the source data used.
_EXPORTABLE_TOP_LEVEL_KEYS = ("APP", "API", "LOG", "SERVICE", "REPOSITORY", "FEATURE_FLAGS")


def _build_app_cfg() -> AppCfg:
    set_env_variables(AppType.COMMONDB, DevIdpConfig.NONE, DevRepositoryConfig.DICT_EMPTY)
    os.environ["COMMONDB_LOG_LEVEL"] = "WARNING"
    return AppCfg("COMMONDB", ServiceType, RepositoryType, log_any=False)


def test_to_dict_unresolved_contains_known_top_level_keys() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    assert set(payload.keys()) == set(_EXPORTABLE_TOP_LEVEL_KEYS)
    assert payload["APP"]["port"] == 8010
    assert payload["REPOSITORY"]["defaults"]["type"] == "DICT"


def test_to_dict_unresolved_values_are_plain_strings_not_resolved_objects() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=False)

    # Pre-validation snapshot: module/class_name stay strings, no injected
    # "class" key from _init_validate_settings's resolution step.
    auth_entry = cast(dict[str, Any], payload["SERVICE"]["auth"])
    assert isinstance(auth_entry["module"], str)
    assert "class" not in auth_entry


def test_to_dict_resolved_stringifies_non_serializable_values() -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=True)

    auth_entry = cast(dict[str, Any], payload["SERVICE"]["auth"])
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
    assert parsed["APP"]["port"] == 8010


def test_to_toml_without_path_returns_text_only() -> None:
    app_cfg = _build_app_cfg()

    text = app_cfg.to_toml()

    assert tomllib.loads(text)["APP"]["port"] == 8010


@pytest.mark.parametrize("resolved", [True, False])
def test_to_dict_filters_to_known_keys_only(resolved: bool) -> None:
    app_cfg = _build_app_cfg()

    payload = app_cfg.to_dict(resolved=resolved)

    assert set(payload.keys()) <= set(_EXPORTABLE_TOP_LEVEL_KEYS)
