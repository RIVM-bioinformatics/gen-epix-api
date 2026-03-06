"""
Runtime-oriented logging contracts.

These tests complement static YAML-shape checks by validating:
  1) class import paths in YAML are importable (formatters/filters)
  2) dictConfig + uvicorn.access emission produces informative access messages
     and structured http fields that downstream platforms can project
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).parents[4]

_PRODUCTION_YAML_PATHS = [
    _REPO_ROOT / "gen_epix" / "casedb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "seqdb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "omopdb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "commondb" / "config" / "logging.yaml",
]
_DEBUG_YAML_PATHS = [
    _REPO_ROOT / "gen_epix" / "casedb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "seqdb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "omopdb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "commondb" / "config" / "logging.debug.yaml",
]
_E2E_YAML_PATHS = [
    _REPO_ROOT / "test" / "end_to_end" / "casedb_seqdb_connection" / "logging.yaml",
]

_ALL_YAML_PATHS = _PRODUCTION_YAML_PATHS + _DEBUG_YAML_PATHS + _E2E_YAML_PATHS


def _load_class(path: str) -> object:
    module_name, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _emit_access_payload_via_dictconfig(yaml_path: Path) -> dict:
    script = textwrap.dedent(
        """
        import json
        import logging
        import logging.config
        import sys
        from pathlib import Path

        import yaml

        config_path = Path(sys.argv[1])
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        # Keep formatter/filter wiring but route all output through one console handler
        # so this runtime contract stays side-effect free (no debug file writes).
        config["handlers"] = {
            "capture": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        }
        for logger_cfg in config.get("loggers", {}).values():
            logger_cfg["handlers"] = ["capture"]
            logger_cfg["propagate"] = False
        root_cfg = config.get("root", {})
        root_cfg["handlers"] = ["capture"]
        root_cfg["level"] = "DEBUG"
        config["root"] = root_cfg

        logging.config.dictConfig(config)
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.info(
            '%s - "%s %s HTTP/%s" %d',
            "127.0.0.1:12345",
            "GET",
            "/runtime-check",
            "1.1",
            204,
        )
        """
    )

    proc = subprocess.run(
        [sys.executable, "-c", script, str(yaml_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert (
        proc.returncode == 0
    ), f"Subprocess failed for {yaml_path.name}: {proc.stderr}"

    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise AssertionError(f"No JSON log line emitted for {yaml_path.name}")


def _emit_app_lifecycle_payloads_via_dictconfig(yaml_path: Path) -> list[dict]:
    script = textwrap.dedent(
        """\
        import logging
        import logging.config
        import sys
        from pathlib import Path

        import yaml

        config_path = Path(sys.argv[1])
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        config["handlers"] = {
            "capture": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        }
        for logger_cfg in config.get("loggers", {}).values():
            logger_cfg["handlers"] = ["capture"]
            logger_cfg["propagate"] = False
            logger_cfg["level"] = "DEBUG"
        root_cfg = config.get("root", {})
        root_cfg["handlers"] = ["capture"]
        root_cfg["level"] = "DEBUG"
        config["root"] = root_cfg

        logging.config.dictConfig(config)

        app_logger_name = next(
            (name for name in config.get("loggers", {}) if name.endswith(".app")),
            "casedb.app",
        )
        logger = logging.getLogger(app_logger_name)
        logger.info(
            '{"code":"e8aafcec","msg":"STARTING_APP","app":{"id":"app-123","name":"CASEDB"}}'
        )
        logger.info(
            '{"code":"e94cad9b","msg":"STARTED_COMMAND","command":{"class":"DemoCommand","id":"cmd-123","user_id":"u-123"}}'
        )
        logger.debug(
            '{"code":"e94cad9b","msg":"STARTED_COMMAND","command":{"class":"DemoCommand","object":{"id":"cmd-obj-123"},"parent_command_id":null,"stack_trace":"DemoCommand"}}'
        )
        """
    )

    proc = subprocess.run(
        [sys.executable, "-c", script, str(yaml_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert (
        proc.returncode == 0
    ), f"Subprocess failed for {yaml_path.name}: {proc.stderr}"

    payloads: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            payloads.append(json.loads(line))

    assert payloads, f"No JSON log lines emitted for {yaml_path.name}"
    return payloads


@pytest.mark.parametrize(
    "yaml_path", _ALL_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_logging_yaml_formatter_and_filter_paths_are_importable(
    yaml_path: Path,
) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    for formatter_cfg in config.get("formatters", {}).values():
        class_path = formatter_cfg.get("()")
        if class_path:
            loaded = _load_class(class_path)
            assert loaded is not None

    for filter_cfg in config.get("filters", {}).values():
        class_path = filter_cfg.get("()")
        if class_path:
            loaded = _load_class(class_path)
            assert loaded is not None


@pytest.mark.parametrize(
    "yaml_path",
    _PRODUCTION_YAML_PATHS + _E2E_YAML_PATHS,
    ids=lambda p: f"runtime-{p.parent.parent.name}",
)
def test_runtime_uvicorn_access_log_is_informative_for_downstream_logmessage(
    yaml_path: Path,
) -> None:
    payload = _emit_access_payload_via_dictconfig(yaml_path)

    assert payload["logger"] == "uvicorn.access"
    assert payload["level"] == "INFO"
    assert payload["message"] == "http.access GET /runtime-check 204"
    assert payload["message"] != "http.access"

    assert payload["http"]["method"] == "GET"
    assert payload["http"]["path"] == "/runtime-check"
    assert payload["http"]["status"] == 204

    # Azure/Grafana commonly project level + message for display columns.
    assert f'{payload["level"]} {payload["message"]}' == (
        "INFO http.access GET /runtime-check 204"
    )


@pytest.mark.parametrize(
    "yaml_path",
    _PRODUCTION_YAML_PATHS + _E2E_YAML_PATHS,
    ids=lambda p: f"runtime-app-{p.parent.parent.name}",
)
def test_runtime_app_lifecycle_logs_have_message_and_operational_aliases(
    yaml_path: Path,
) -> None:
    payloads = _emit_app_lifecycle_payloads_via_dictconfig(yaml_path)

    startup = next((x for x in payloads if x.get("code") == "e8aafcec"), None)
    assert startup is not None
    assert startup["msg"] == "STARTING_APP"
    assert startup["message"] == "STARTING_APP"
    assert startup["app"]["id"] == "app-123"
    assert startup["app_id"] == "app-123"

    command_info = next(
        (
            x
            for x in payloads
            if x.get("code") == "e94cad9b"
            and isinstance(x.get("command"), dict)
            and x["command"].get("id") == "cmd-123"
        ),
        None,
    )
    assert command_info is not None
    assert command_info["message"] == "STARTED_COMMAND"
    assert command_info["command_id"] == "cmd-123"

    command_debug = next(
        (
            x
            for x in payloads
            if x.get("code") == "e94cad9b"
            and isinstance(x.get("command"), dict)
            and isinstance(x["command"].get("object"), dict)
            and x["command"]["object"].get("id") == "cmd-obj-123"
        ),
        None,
    )
    assert command_debug is not None
    assert command_debug["message"] == "STARTED_COMMAND"
    assert command_debug["command_id"] == "cmd-obj-123"
