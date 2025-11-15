import json
import os
from pathlib import Path


def set_envvar() -> None:
    path = Path(__file__).parent
    casedb_settings_files: list[Path] = [
        path / "casedb.settings.toml",
        path / "casedb.settings.repository.toml",
        path / "casedb.secrets.service.toml",
        path / "casedb.secrets.repository.toml",
        path / "identity_provider.toml",
    ]
    seqdb_settings_files: list[Path] = [
        path / "seqdb.settings.toml",
        path / "seqdb.settings.repository.toml",
        path / "seqdb.secrets.service.toml",
        path / "seqdb.secrets.repository.toml",
        path / "identity_provider.toml",
    ]
    log_config_file = path / "logging.yaml"

    os.environ["CASEDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in casedb_settings_files]
    )
    os.environ["SEQDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in seqdb_settings_files]
    )
    os.environ["CASEDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    os.environ["SEQDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    os.environ["LOG_LEVEL"] = "ERROR"


# app_cfg = AppCfg(AppType.CASEDB, ServiceType, RepositoryType, log_setup=False)
# app_composer = AppComposer(app_cfg)
# app = app_composer.app
