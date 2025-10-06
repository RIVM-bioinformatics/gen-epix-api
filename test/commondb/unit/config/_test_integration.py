"""Integration test for the complete configuration system."""

import os
from enum import Enum
from pathlib import Path
from typing import Generator, Tuple

import pytest


# We'll need to create mock enums for the test since we don't have access to the real ones
class MockServiceType(Enum):
    AUTH = "auth"
    RBAC = "rbac"
    CASE = "case"


class MockRepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


@pytest.fixture
def config_dirs() -> tuple[Path, Path]:
    """Provide config and data directories."""
    config_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "gen_epix"
        / "commondb"
        / "config"
    )
    data_dir = Path(__file__).parent / "data"
    return config_dir, data_dir


@pytest.fixture
def clean_environment() -> Generator[None, None, None]:
    """Clean environment fixture that restores original environment after test."""
    original_env = dict(os.environ)
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_complete_configuration_system_with_examples(
    config_dirs: tuple[Path, Path], clean_environment: None
) -> None:
    """Test the complete configuration system using example files."""
    config_dir, data_dir = config_dirs

    # Set up logging config file (required)
    logging_config_file = config_dir / "logging.yaml"
    os.environ["COMMONDB_LOGGING_CONFIG_FILE"] = str(logging_config_file)

    # Set up custom settings file
    custom_settings_file = data_dir / "settings-custom.toml"
    os.environ["COMMONDB_SETTINGS_FILE"] = str(custom_settings_file)

    # Set up file secrets
    secrets_files_dir = data_dir / "secrets" / "files"
    os.environ["COMMONDB_SECRETS_STRATEGY"] = "file"
    os.environ["COMMONDB_SECRETS_PATH"] = str(secrets_files_dir)

    # Import here to avoid issues during test collection
    try:
        from gen_epix.commondb.config.cfg import AppCfg

        # Create the configuration
        app_cfg = AppCfg(
            app_name="commondb",
            service_type_enum=MockServiceType,
            repository_type_enum=MockRepositoryType,
            log_setup=False,  # Disable logging setup for test
        )

        # Test settings access - values from custom settings file should override defaults
        # Custom settings file has host="127.0.0.1", port=9000, debug=true, default_route="/api-docs"
        assert app_cfg.cfg.app.host == "127.0.0.1"
        assert app_cfg.cfg.app.port == 9000
        assert app_cfg.cfg.app.debug is True
        assert app_cfg.cfg.api.default_route == "/api-docs"

        # Test secrets access
        assert app_cfg.secrets["db"]["repository_type"] == "DICT"
        assert (
            app_cfg.secrets["root"]["user"]["id"]
            == "01915051-edde-f225-19d7-7ab8886e00bc"
        )
        assert app_cfg.secrets["root"]["user"]["email"] == "root@dummy.org"

        # Test backward compatibility through cfg property
        assert app_cfg.cfg.app.host == "127.0.0.1"
        assert app_cfg.cfg.secret.db.repository_type == "DICT"
        assert app_cfg.cfg.secret.root.user.email == "root@dummy.org"

    except ImportError as e:
        pytest.skip(f"Could not import required modules: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
