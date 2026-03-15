from __future__ import annotations

import json
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import pytest

_REPO_ROOT = Path(__file__).parents[4]
_APP_IMPORT_SPECS = {
    "CASEDB": {
        "module_name": "gen_epix.casedb.app",
        "default_auto_create_new_users": True,
    },
    "SEQDB": {
        "module_name": "gen_epix.seqdb.app",
        "default_auto_create_new_users": True,
    },
    "OMOPDB": {
        "module_name": "gen_epix.omopdb.app",
        "default_auto_create_new_users": False,
    },
}


def _run_app_import_smoke(
    app_name: str,
    extra_settings_files: list[Path] | None = None,
) -> dict:
    script = textwrap.dedent(
        """\
        import importlib
        import json
        import sys
        from pathlib import Path

        from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
        from gen_epix.commondb.domain.util import set_env_variables

        app_name = sys.argv[1]
        extra_settings_files = [Path(arg) for arg in sys.argv[2:]]
        module_name = f"gen_epix.{app_name.lower()}.app"

        set_env_variables(
            AppType[app_name],
            DevIdpConfig.NONE,
            DevRepositoryConfig.DICT_EMPTY,
            extra_settings_files=extra_settings_files or None,
        )

        module = importlib.import_module(module_name)
        auth_service = module.APP_COMPOSER.services[module.enum.ServiceType.AUTH]
        auth_props = module.APP_CFG.cfg["service"]["auth"]["props"]

        payload = {
            "module_name": module.__name__,
            "has_app_cfg": hasattr(module, "APP_CFG"),
            "has_app_composer": hasattr(module, "APP_COMPOSER"),
            "has_fast_api": hasattr(module, "FAST_API"),
            "app_cfg_type": type(getattr(module, "APP_CFG", None)).__name__,
            "app_composer_type": type(getattr(module, "APP_COMPOSER", None)).__name__,
            "fast_api_type": type(getattr(module, "FAST_API", None)).__name__,
            "cfg_auto_create_new_users": auth_props["auto_create_new_users"],
            "cfg_root_token_time_to_live": auth_props["root_token_time_to_live"],
            # TODO: Expose these resolved startup values via a public read-only AuthService API and stop asserting private attributes here.
            "service_auto_create_new_users": auth_service._auto_create_new_users,
            "service_root_token_time_to_live": auth_service._root_token_time_to_live,
            "service_idp_client_count": len(auth_service.idp_clients),
        }
        print(json.dumps(payload))
        """
    )

    args = [sys.executable, "-c", script, app_name]
    if extra_settings_files:
        args.extend(str(path) for path in extra_settings_files)

    proc = subprocess.run(
        args,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, (
        f"{app_name.lower()} import smoke subprocess failed\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )

    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            if "module_name" in payload:
                return payload

    raise AssertionError(
        f"{app_name.lower()} import smoke subprocess did not emit JSON payload\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )


@pytest.fixture  # Added fixture to create a temp folder for override files, to isolate test artifacts
def override_tmp_dir() -> Iterator[Path]:
    tmp_dir = _REPO_ROOT / ".tmp-test-artifacts" / "app_import_smoke" / uuid4().hex
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(
            tmp_dir, ignore_errors=True
        )  # Added teardown cleanup to remove temporary files after tests are done


def _write_string_auth_override_file(override_tmp_dir: Path, app_name: str) -> Path:
    override_path = override_tmp_dir / f"{app_name.lower()}.toml"
    override_path.write_text(
        textwrap.dedent(
            """\
            [service.auth.props]
            auto_create_new_users = "0"
            root_token_time_to_live = "900"
            """
        ),
        encoding="utf-8",
    )
    return override_path


def _assert_default_import_payload(payload: dict, app_name: str) -> None:
    spec = _APP_IMPORT_SPECS[app_name]

    assert payload["module_name"] == spec["module_name"]
    assert payload["has_app_cfg"] is True
    assert payload["has_app_composer"] is True
    assert payload["has_fast_api"] is True
    assert payload["app_cfg_type"] == "AppCfg"
    assert payload["app_composer_type"] == "AppComposer"
    assert payload["fast_api_type"] == "FastAPI"
    assert payload["cfg_auto_create_new_users"] is spec["default_auto_create_new_users"]
    assert payload["cfg_root_token_time_to_live"] == 900
    assert (
        payload["service_auto_create_new_users"]
        is spec["default_auto_create_new_users"]
    )
    assert payload["service_root_token_time_to_live"] == 900
    assert payload["service_idp_client_count"] == 0


def _assert_string_override_payload(payload: dict, app_name: str) -> None:
    spec = _APP_IMPORT_SPECS[app_name]

    assert payload["module_name"] == spec["module_name"]
    assert payload["has_app_cfg"] is True
    assert payload["has_app_composer"] is True
    assert payload["has_fast_api"] is True
    assert payload["app_cfg_type"] == "AppCfg"
    assert payload["app_composer_type"] == "AppComposer"
    assert payload["fast_api_type"] == "FastAPI"
    assert payload["cfg_auto_create_new_users"] == "0"
    assert payload["cfg_root_token_time_to_live"] == "900"
    assert payload["service_auto_create_new_users"] is False
    assert payload["service_root_token_time_to_live"] == 900
    assert payload["service_idp_client_count"] == 0


def test_casedb_import_smoke_defaults() -> None:
    payload = _run_app_import_smoke("CASEDB")

    _assert_default_import_payload(payload, "CASEDB")


def test_casedb_import_smoke_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "CASEDB")

    payload = _run_app_import_smoke("CASEDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "CASEDB")


def test_seqdb_import_smoke_defaults() -> None:
    payload = _run_app_import_smoke("SEQDB")

    _assert_default_import_payload(payload, "SEQDB")


def test_seqdb_import_smoke_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "SEQDB")

    payload = _run_app_import_smoke("SEQDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "SEQDB")


def test_omopdb_import_smoke_defaults() -> None:
    payload = _run_app_import_smoke("OMOPDB")

    _assert_default_import_payload(payload, "OMOPDB")


def test_omopdb_import_smoke_string_auth_overrides(override_tmp_dir: Path) -> None:
    override_file = _write_string_auth_override_file(override_tmp_dir, "OMOPDB")

    payload = _run_app_import_smoke("OMOPDB", extra_settings_files=[override_file])

    _assert_string_override_payload(payload, "OMOPDB")
