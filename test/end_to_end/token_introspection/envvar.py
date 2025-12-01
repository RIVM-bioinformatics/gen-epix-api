import json
import os
from pathlib import Path


def set_envvar() -> None:
    path = Path(__file__).parent
    commondb_settings_files: list[Path] = [
        path / "commondb.settings.toml",
        path / "commondb.settings.repository.toml",
        path / "commondb.secrets.service.toml",
        path / "commondb.secrets.repository.toml",
        path / "identity_provider.toml",
    ]
    log_config_file = path / "logging.yaml"

    os.environ["COMMONDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in commondb_settings_files]
    )
    os.environ["COMMONDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    os.environ["COMMONDB_LOG_LEVEL"] = "INFO"
