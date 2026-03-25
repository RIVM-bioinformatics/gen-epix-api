"""
Contract tests for all production logging.yaml configuration files.

These tests validate the structural requirements that must hold across every
service's logging config:
  - root: block is present and routes through the console handler
  - third-party loggers are explicitly configured with deliberate levels:
      sqlalchemy.engine/pool -> WARNING (INFO emits full SQL text, PII risk)
      httpx               -> INFO    (redirects/auth events are operationally relevant)
      asyncio             -> WARNING (INFO is pure event-loop infra, not actionable)
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

# Maps each explicitly managed third-party logger to its intended minimum level.
# Change here when the YAML changes so the contract stays in sync.
_THIRD_PARTY_LOGGERS: dict[str, str] = {
    "sqlalchemy.engine": "WARNING",  # INFO = full SQL text per query (verbose, PII risk)
    "sqlalchemy.pool": "WARNING",  # INFO = connection checkout/checkin noise
    "httpx": "INFO",  # redirects and auth events arrive at INFO
    "asyncio": "WARNING",  # INFO/DEBUG is event-loop internals
}


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_third_party_loggers_explicitly_configured(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    loggers = config.get("loggers", {})

    for name, expected_level in _THIRD_PARTY_LOGGERS.items():
        assert (
            name in loggers
        ), f"Third-party logger '{name}' not explicitly configured in {yaml_path.name}"
        entry = loggers[name]
        assert (
            entry.get("propagate") is False
        ), f"Logger '{name}' must have propagate: false in {yaml_path.name}"
        assert (
            entry.get("level") == expected_level
        ), f"Logger '{name}' must be set to {expected_level} in {yaml_path.name}"
        assert "console" in entry.get(
            "handlers", []
        ), f"Logger '{name}' must use the console handler in {yaml_path.name}"


@pytest.mark.scenario_ids("TC-LOG-01-01")
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
        == "gen_epix.commondb.config.json_logging.UvicornAccessLogFilter"
    )
    assert loggers.get("uvicorn.access", {}).get("filters") == [
        "uvicorn_access_structured"
    ], f"uvicorn.access must declare filters: [uvicorn_access_structured] in {yaml_path.name}"


@pytest.mark.scenario_ids("TC-LOG-01-01")
@pytest.mark.parametrize(
    "yaml_path", PRODUCTION_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_console_handler_uses_json_formatter(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    handlers = config.get("handlers", {})
    formatters = config.get("formatters", {})
    json_formatter_cfg = formatters.get("json", {})

    assert handlers.get("console", {}).get("formatter") == "json"
    assert (
        json_formatter_cfg.get("()")
        == "gen_epix.commondb.config.json_logging.JsonFormatter"
    )
    assert json_formatter_cfg.get("redacted_value") == "[REDACTED]"
    sensitive_keys = json_formatter_cfg.get("sensitive_keys")
    assert isinstance(sensitive_keys, list)
    assert "client_secret" in sensitive_keys
