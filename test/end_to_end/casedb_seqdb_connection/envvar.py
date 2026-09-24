import json
import os
from pathlib import Path


def set_envvar(identity_provider_file: Path | None = None) -> None:
    path = Path(__file__).parent
    identity_provider_file = identity_provider_file or path / "identity_provider.toml"
    casedb_settings_files: list[Path] = [
        path / "casedb.settings.toml",
        path / "casedb.feature_flags.toml",
        path / "casedb.settings.repository.toml",
        path / "casedb.secrets.service.toml",
        path / "casedb.secrets.repository.toml",
        identity_provider_file,
    ]
    seqdb_settings_files: list[Path] = [
        path / "seqdb.settings.toml",
        path / "seqdb.feature_flags.toml",
        path / "seqdb.settings.repository.toml",
        path / "seqdb.secrets.service.toml",
        path / "seqdb.secrets.repository.toml",
        identity_provider_file,
    ]
    omop_settings_files: list[Path] = [
        path / "omopdb.settings.toml",
        path / "omopdb.feature_flags.toml",
        path / "omopdb.settings.repository.toml",
        path / "omopdb.secrets.service.toml",
        path / "omopdb.secrets.repository.toml",
        identity_provider_file,
    ]

    log_config_file = path / "logging.yaml"

    os.environ["CASEDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in casedb_settings_files]
    )
    os.environ["SEQDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in seqdb_settings_files]
    )
    os.environ["OMOPDB_SETTINGS_FILES"] = json.dumps(
        [x.absolute().as_posix() for x in omop_settings_files]
    )
    os.environ["CASEDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    os.environ["SEQDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    os.environ["OMOPDB_LOG_CONFIG_FILE"] = log_config_file.absolute().as_posix()
    # os.environ["CASEDB_LOG_LEVEL"] = "DEBUG"
    # os.environ["SEQDB_LOG_LEVEL"] = "DEBUG"
    os.environ["CASEDB_LOG_LEVEL"] = "WARNING"
    os.environ["SEQDB_LOG_LEVEL"] = "WARNING"
    os.environ["OMOPDB_LOG_LEVEL"] = "WARNING"
