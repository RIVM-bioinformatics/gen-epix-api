"""
Contract tests for all production logging.yaml configuration files.

These tests validate the structural requirements that must hold across every
service's logging config:
  - root: block is present and routes through the console handler
  - third-party loggers (sqlalchemy, httpx, asyncio) are explicitly silenced
    at WARNING level with propagate: false so they emit valid JSON and don't
    flood Grafana with INFO noise
  - uvicorn.access carries the structured access-log filter
  - the JSON formatter and UvicornAccessLogFilter class references are correct
"""

from pathlib import Path

import pytest
import yaml

# Absolute paths to the four production logging YAML files
_REPO_ROOT = Path(__file__).parents[4]
PRODUCTION_YAML_PATHS = [
    _REPO_ROOT / "gen_epix" / "casedb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "seqdb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "omopdb" / "config" / "logging.yaml",
    _REPO_ROOT / "gen_epix" / "commondb" / "config" / "logging.yaml",
]

_THIRD_PARTY_LOGGERS = ["sqlalchemy.engine", "sqlalchemy.pool", "httpx", "asyncio"]


@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_root_logger_is_present_and_uses_console_handler(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    root = config.get("root")
    assert root is not None, f"root: block missing in {yaml_path.name}"
    assert "console" in root.get(
        "handlers", []
    ), f"root logger must route through console handler in {yaml_path.name}"


@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_third_party_loggers_explicitly_configured(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    loggers = config.get("loggers", {})

    for name in _THIRD_PARTY_LOGGERS:
        assert (
            name in loggers
        ), f"Third-party logger '{name}' not explicitly configured in {yaml_path.name}"
        entry = loggers[name]
        assert (
            entry.get("propagate") is False
        ), f"Logger '{name}' must have propagate: false in {yaml_path.name}"
        assert (
            entry.get("level") == "WARNING"
        ), f"Logger '{name}' must be set to WARNING in {yaml_path.name}"
        assert "console" in entry.get(
            "handlers", []
        ), f"Logger '{name}' must use the console handler in {yaml_path.name}"


@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_uvicorn_access_has_structured_filter(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    loggers = config.get("loggers", {})
    filters = config.get("filters", {})

    assert (
        "uvicorn_access_structured" in filters
    ), f"uvicorn_access_structured filter missing in {yaml_path.name}"
    assert (
        filters["uvicorn_access_structured"]["()"]
        == "gen_epix.commondb.domain.json_logging.UvicornAccessLogFilter"
    )
    assert loggers.get("uvicorn.access", {}).get("filters") == [
        "uvicorn_access_structured"
    ], f"uvicorn.access must declare filters: [uvicorn_access_structured] in {yaml_path.name}"


@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_console_handler_uses_json_formatter(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    handlers = config.get("handlers", {})
    formatters = config.get("formatters", {})

    assert handlers.get("console", {}).get("formatter") == "json"
    assert (
        formatters.get("json", {}).get("()")
        == "gen_epix.commondb.domain.json_logging.JsonFormatter"
    )
