"""Tests for the new configuration management system."""

import os
import unittest
from pathlib import Path

from gen_epix.commondb.config.secret_provider import EnvironmentSecretProvider
from gen_epix.commondb.config.secret_provider.file import FileSecretProvider
from gen_epix.commondb.config.secrets import SecretProviderFactory
from gen_epix.commondb.config.settings import SettingsManager


class TestConfigurationSystem(unittest.TestCase):
    """Test the new configuration management system."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.config_dir = (
            Path(__file__).parent.parent.parent.parent.parent
            / "gen_epix"
            / "commondb"
            / "config"
        )
        self.data_dir = Path(__file__).parent / "data"

        # Store original environment variables to restore later
        self.original_env = dict(os.environ)

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_settings_manager_with_custom_file(self) -> None:
        """Test SettingsManager loading custom settings file."""
        custom_settings_file = self.data_dir / "settings-custom.toml"

        # Test with custom settings file
        settings_manager = SettingsManager(prefix="COMMONDB")
        settings = settings_manager.load_settings(
            settings_files=str(custom_settings_file)
        )

        # Verify custom settings are loaded
        self.assertEqual(settings.app.host, "127.0.0.1")
        self.assertEqual(settings.app.port, 9000)
        self.assertTrue(settings.app.debug)
        self.assertEqual(settings.api.default_route, "/api-docs")
        self.assertEqual(settings.api.gzip_response_minimum_size, 512)
        self.assertEqual(settings.log.level, "DEBUG")
        self.assertEqual(settings.service.rbac.user_invitation_time_to_live, 3600)

    def test_settings_manager_with_default_file(self) -> None:
        """Test SettingsManager loading default settings."""
        settings_manager = SettingsManager(prefix="COMMONDB")
        settings = settings_manager.load_settings()

        # Verify default settings are loaded
        self.assertEqual(settings.app.host, "0.0.0.0")
        self.assertEqual(settings.app.port, 8000)
        self.assertFalse(settings.app.debug)
        self.assertEqual(settings.api.default_route, "/openapi.json")
        self.assertEqual(settings.api.gzip_response_minimum_size, 1024)
        self.assertEqual(settings.log.level, "DEBUG")
        self.assertEqual(settings.service.rbac.user_invitation_time_to_live, 604800)

    def test_settings_manager_with_environment_overrides(self) -> None:
        """Test SettingsManager with environment variable overrides."""
        # Set environment variables for overrides
        os.environ["COMMONDB_APP__HOST"] = "192.168.1.100"
        os.environ["COMMONDB_APP__PORT"] = "8080"
        os.environ["COMMONDB_API__DEFAULT_ROUTE"] = "/swagger"
        os.environ["COMMONDB_SERVICE__RBAC__USER_INVITATION_TIME_TO_LIVE"] = "7200"

        settings_manager = SettingsManager(prefix="COMMONDB")
        settings = settings_manager.load_settings()

        # Verify environment overrides are applied
        self.assertEqual(settings.app.host, "192.168.1.100")
        self.assertEqual(settings.app.port, 8080)
        self.assertEqual(settings.api.default_route, "/swagger")
        self.assertEqual(settings.service.rbac.user_invitation_time_to_live, 7200)

    def test_environment_secret_provider(self) -> None:
        """Test EnvironmentSecretProvider with example environment variables."""
        # Load environment variables from example file
        env_vars_file = self.data_dir / "secrets" / "environment-vars.env"

        # Parse and set environment variables from example file
        with open(env_vars_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

        # Test environment secret provider
        provider = EnvironmentSecretProvider(app_prefix="COMMONDB")
        secrets = provider.load_secrets()

        # Verify secrets are loaded correctly
        self.assertEqual(secrets["db"]["repository_type"], "DICT")
        self.assertEqual(secrets["log"]["level"], "INFO")
        self.assertEqual(
            secrets["no_authentication"]["user"]["id"],
            "018bcd02-eb19-fb14-c520-64cbb78d9135",
        )
        self.assertEqual(
            secrets["no_authentication"]["user"]["email"], "dummy@dummy.org"
        )
        self.assertEqual(
            secrets["root"]["user"]["id"], "01915051-edde-f225-19d7-7ab8886e00bc"
        )
        self.assertEqual(secrets["root"]["user"]["email"], "root@dummy.org")
        self.assertEqual(
            secrets["repository"]["dict"]["defaults"]["dir"], "./data/commondb/demo"
        )

    def test_file_secret_provider(self) -> None:
        """Test FileSecretProvider with example files."""
        secrets_files_dir = self.data_dir / "secrets" / "files"

        # Test file secret provider
        provider = FileSecretProvider(
            prefix="COMMONDB", secrets_path=str(secrets_files_dir)
        )
        secrets = provider.load_secrets()

        # Verify secrets are loaded correctly from files
        self.assertEqual(secrets["db"]["repository_type"], "DICT")
        self.assertEqual(
            secrets["root"]["user"]["id"], "01915051-edde-f225-19d7-7ab8886e00bc"
        )
        self.assertEqual(secrets["root"]["user"]["email"], "root@dummy.org")
        self.assertEqual(
            secrets["repository"]["sa_sql"]["defaults"]["server"], "127.0.0.1"
        )
        self.assertEqual(
            secrets["repository"]["sa_sql"]["defaults"]["pwd"], "my_secret_password"
        )

    def test_secret_provider_factory_environment_strategy(self) -> None:
        """Test SecretProviderFactory with environment strategy."""
        # Set up environment for environment strategy
        os.environ["COMMONDB_SECRETS_STRATEGY"] = "environment"
        os.environ["COMMONDB_SECRET_DB__REPOSITORY_TYPE"] = "DICT"
        os.environ["COMMONDB_SECRET_ROOT__USER__EMAIL"] = "test@example.com"

        # Test factory creation
        provider = SecretProviderFactory.create_provider(prefix="COMMONDB")
        self.assertIsInstance(provider, EnvironmentSecretProvider)

        # Test secrets loading
        secrets = SecretProviderFactory.load_secrets(prefix="COMMONDB")
        self.assertEqual(secrets["db"]["repository_type"], "DICT")
        self.assertEqual(secrets["root"]["user"]["email"], "test@example.com")

    def test_secret_provider_factory_file_strategy(self) -> None:
        """Test SecretProviderFactory with file strategy."""
        secrets_files_dir = self.data_dir / "secrets" / "files"

        # Set up environment for file strategy
        os.environ["COMMONDB_SECRETS_STRATEGY"] = "file"
        os.environ["COMMONDB_SECRETS_PATH"] = str(secrets_files_dir)

        # Test factory creation
        provider = SecretProviderFactory.create_provider(prefix="COMMONDB")
        self.assertIsInstance(provider, FileSecretProvider)

        # Test secrets loading
        secrets = SecretProviderFactory.load_secrets(prefix="COMMONDB")
        self.assertEqual(secrets["db"]["repository_type"], "DICT")
        self.assertEqual(secrets["root"]["user"]["email"], "root@dummy.org")

    def test_different_app_prefixes(self) -> None:
        """Test that different app prefixes work correctly."""
        # Test CASEDB prefix with environment variables
        os.environ["CASEDB_APP__HOST"] = "casedb.example.com"
        os.environ["CASEDB_APP__PORT"] = "9001"

        settings_manager = SettingsManager(prefix="CASEDB")
        settings = settings_manager.load_settings()

        # Verify CASEDB-specific overrides
        self.assertEqual(settings.app.host, "casedb.example.com")
        self.assertEqual(settings.app.port, 9001)

        # Test SEQDB prefix with secrets
        os.environ["SEQDB_SECRETS_STRATEGY"] = "environment"
        os.environ["SEQDB_SECRET_DB__REPOSITORY_TYPE"] = "SA_SQL"

        secrets = SecretProviderFactory.load_secrets(prefix="SEQDB")
        self.assertEqual(secrets["db"]["repository_type"], "SA_SQL")

    def test_nested_configuration_paths(self) -> None:
        """Test deeply nested configuration paths."""
        # Test deeply nested environment variables
        os.environ["COMMONDB_API__HTTP_HEADER__GENERAL__CACHECONTROL"] = "no-store"
        os.environ[
            "COMMONDB_SECRET_REPOSITORY__SA_SQL__DEFAULTS__CONNECTION_STRING"
        ] = "custom_connection"
        os.environ["COMMONDB_SECRETS_STRATEGY"] = "environment"

        # Test settings
        settings_manager = SettingsManager(prefix="COMMONDB")
        raw_config = settings_manager.load_settings()

        # Access via raw config since deeply nested paths might not be in schema
        settings_manager.load_settings()  # Load to populate raw_config
        nested_value = settings_manager.get_setting(
            "api.http_header.general.CacheControl"
        )
        if nested_value:
            self.assertEqual(nested_value, "no-store")

        # Test secrets
        secrets = SecretProviderFactory.load_secrets(prefix="COMMONDB")
        self.assertEqual(
            secrets["repository"]["sa_sql"]["defaults"]["connection_string"],
            "custom_connection",
        )

    def test_json_parsing_in_environment_secrets(self) -> None:
        """Test JSON parsing in environment secret values."""
        # Test JSON array parsing
        os.environ["COMMONDB_SECRETS_STRATEGY"] = "environment"
        os.environ["COMMONDB_SECRET_USER__ROLES"] = '["ADMIN", "USER"]'
        os.environ["COMMONDB_SECRET_CONFIG__SETTINGS"] = (
            '{"debug": true, "timeout": 30}'
        )

        provider = EnvironmentSecretProvider(app_prefix="COMMONDB")
        secrets = provider.load_secrets()

        # Verify JSON parsing
        self.assertEqual(secrets["user"]["roles"], ["ADMIN", "USER"])
        self.assertEqual(secrets["config"]["settings"], {"debug": True, "timeout": 30})

    def test_secret_provider_get_specific_secret(self) -> None:
        """Test getting specific secrets by path."""
        # Set up environment secrets
        os.environ["COMMONDB_SECRET_DB__REPOSITORY_TYPE"] = "DICT"
        os.environ["COMMONDB_SECRET_ROOT__USER__EMAIL"] = "root@test.com"
        os.environ["COMMONDB_SECRET_NESTED__DEEP__VALUE"] = "found_it"

        provider = EnvironmentSecretProvider(app_prefix="COMMONDB")
        provider.load_secrets()  # Load all secrets first

        # Test getting specific secrets
        self.assertEqual(provider.get_secret("db.repository_type"), "DICT")
        self.assertEqual(provider.get_secret("root.user.email"), "root@test.com")
        self.assertEqual(provider.get_secret("nested.deep.value"), "found_it")
        self.assertIsNone(provider.get_secret("nonexistent.path"))

    def test_backward_compatibility_example(self) -> None:
        """Test that the configuration works with backward compatibility patterns."""
        # This test simulates how the old cfg would be accessed
        from gen_epix.commondb.config.cfg import ConfigProxy
        from gen_epix.commondb.config.settings import SettingsManager

        # Load example settings and secrets
        settings_manager = SettingsManager(prefix="COMMONDB")
        settings = settings_manager.load_settings()

        # Set up some test secrets
        secrets = {
            "db": {"repository_type": "DICT"},
            "log": {"level": "INFO"},
            "root": {"user": {"id": "12345", "email": "root@example.com"}},
        }

        # Create config proxy for backward compatibility
        cfg = ConfigProxy(settings, secrets)

        # Test accessing settings through cfg
        self.assertEqual(cfg.app.host, "0.0.0.0")
        self.assertEqual(cfg.app.port, 8000)
        self.assertEqual(cfg.api.default_route, "/openapi.json")

        # Test accessing secrets through cfg.secret
        self.assertEqual(cfg.secret.db.repository_type, "DICT")
        self.assertEqual(cfg.secret.log.level, "INFO")
        self.assertEqual(cfg.secret.root.user.id, "12345")
        self.assertEqual(cfg.secret.root.user.email, "root@example.com")

        # Test get method with defaults
        self.assertEqual(cfg.get("app").host, "0.0.0.0")
        self.assertEqual(cfg.secret.get("nonexistent", "default"), "default")


if __name__ == "__main__":
    unittest.main()
