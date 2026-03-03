from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).parents[4]
DEBUG_YAML_PATHS = [
    _REPO_ROOT / "gen_epix" / "casedb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "seqdb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "omopdb" / "config" / "logging.debug.yaml",
    _REPO_ROOT / "gen_epix" / "commondb" / "config" / "logging.debug.yaml",
]


@pytest.mark.parametrize(
    "yaml_path", DEBUG_YAML_PATHS, ids=lambda p: p.parent.parent.name
)
def test_debug_console_uses_json_formatter(yaml_path: Path) -> None:
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    handlers = config.get("handlers", {})
    formatters = config.get("formatters", {})
    json_formatter_cfg = formatters.get("json", {})

    assert handlers.get("console", {}).get("formatter") == "json"
    assert handlers.get("file", {}).get("formatter") == "json"
    assert (
        json_formatter_cfg.get("()")
        == "gen_epix.commondb.domain.json_logging.JsonFormatter"
    )
