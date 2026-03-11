import json
import os
from pathlib import Path


def set_envvar() -> None:
    path = Path(__file__).parent
    casedb_settings_files: list[Path] = [
        path / "casedb.settings.toml",
        path / "casedb.feature_flags.toml",
        path / "casedb.settings.repository.toml",
        path / "casedb.secrets.service.toml",
        path / "casedb.secrets.repository.toml",
        path / "identity_provider.toml",
    ]
    seqdb_settings_files: list[Path] = [
        path / "seqdb.settings.toml",
        path / "seqdb.feature_flags.toml",
        path / "seqdb.settings.repository.toml",
        path / "seqdb.secrets.service.toml",
        path / "seqdb.secrets.repository.toml",
        path / "identity_provider.toml",
    ]
    omop_settings_files: list[Path] = [
        path / "omop.settings.toml",
        path / "omop.feature_flags.toml",
        path / "omop.settings.repository.toml",
        path / "omop.secrets.service.toml",
        path / "omop.secrets.repository.toml",
        path / "identity_provider.toml",
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


def get_contract_env_overrides() -> dict[str, str]:
    path = Path(__file__).parent
    casedb_settings_files: list[Path] = [
        path / "casedb.settings.toml",
        path / "casedb.settings.repository.toml",
        path / "contract.casedb.secrets.service.toml",
        path / "casedb.secrets.repository.toml",
        path / "contract.casedb.identity_provider.toml",
    ]
    seqdb_settings_files: list[Path] = [
        path / "seqdb.settings.toml",
        path / "seqdb.settings.repository.toml",
        path / "contract.seqdb.secrets.service.toml",
        path / "seqdb.secrets.repository.toml",
        path / "contract.seqdb.identity_provider.toml",
    ]
    log_config_file = path / "logging.yaml"

    return {
        "CASEDB_SETTINGS_FILES": json.dumps(
            [x.absolute().as_posix() for x in casedb_settings_files]
        ),
        "SEQDB_SETTINGS_FILES": json.dumps(
            [x.absolute().as_posix() for x in seqdb_settings_files]
        ),
        "CASEDB_LOG_CONFIG_FILE": log_config_file.absolute().as_posix(),
        "SEQDB_LOG_CONFIG_FILE": log_config_file.absolute().as_posix(),
        "CASEDB_LOG_LEVEL": "WARNING",
        "SEQDB_LOG_LEVEL": "WARNING",
    }


def set_contract_envvar() -> None:
    for key, value in get_contract_env_overrides().items():
        os.environ[key] = value
