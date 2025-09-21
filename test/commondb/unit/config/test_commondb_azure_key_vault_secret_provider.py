"""Tests for AzureKeyVaultSecretProvider."""

from unittest.mock import Mock, patch

import pytest

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider import (
    AzureKeyVaultSecretProvider,
    SecretLoadError,
)


class MockSecretProperty:
    """Mock for Azure Key Vault secret property."""

    def __init__(self, name: str | None) -> None:
        self.name = name


class MockSecret:
    """Mock for Azure Key Vault secret."""

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value


class TestAzureKeyVaultSecretProvider:
    """Test cases for AzureKeyVaultSecretProvider."""

    @pytest.fixture
    def provider(self) -> AzureKeyVaultSecretProvider:
        """Create a test provider instance."""
        return AzureKeyVaultSecretProvider(prefix="TEST_")

    def test_init_with_default_parameters(self) -> None:
        """Test provider initialization with default parameters."""
        provider = AzureKeyVaultSecretProvider(prefix="TEST_")

        assert provider.prefix == "TEST_"
        assert provider.lowercase_keys is True
        assert provider._client is None
        assert provider._secrets_cache is None

    def test_init_with_custom_parameters(self) -> None:
        """Test provider initialization with custom parameters."""
        provider = AzureKeyVaultSecretProvider(prefix="CUSTOM_", lowercase_keys=False)

        assert provider.prefix == "CUSTOM_"
        assert provider.lowercase_keys is False
        assert provider._client is None
        assert provider._secrets_cache is None

    def test_inheritance_from_base_secret_provider(
        self, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test that provider properly inherits from BaseSecretProvider."""
        from gen_epix.commondb.config.secret_provider.base import BaseSecretProvider

        assert isinstance(provider, BaseSecretProvider)
        assert hasattr(provider, "prefix")
        assert hasattr(provider, "lowercase_keys")
        assert hasattr(provider, "_secrets_cache")
        assert hasattr(provider, "get_secret")
        assert hasattr(provider, "load_secrets")

    def test_constants(self) -> None:
        """Test that environment variable constants are correctly defined."""
        assert AzureKeyVaultSecretProvider.URL_ENV_VAR == "AZURE_KEYVAULT_URL"
        assert AzureKeyVaultSecretProvider.CLIENT_ID_ENV_VAR == "AZURE_CLIENT_ID"
        assert (
            AzureKeyVaultSecretProvider.CLIENT_SECRET_ENV_VAR == "AZURE_CLIENT_SECRET"
        )
        assert AzureKeyVaultSecretProvider.TENANT_ID_ENV_VAR == "AZURE_TENANT_ID"

    @patch("gen_epix.commondb.config.secret_provider.azure_key_vault.os.environ")
    def test_get_client_missing_azure_dependencies(
        self, mock_environ: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test _get_client raises error when Azure dependencies are missing."""
        mock_environ.get.return_value = "https://test-vault.vault.azure.net/"

        # Mock the import to fail by patching __import__
        def mock_import(name, *args, **kwargs):
            if name.startswith("azure."):
                raise ImportError(f"No module named '{name}'")
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(SecretLoadError) as exc_info:
                provider._get_client()

            assert "Azure Key Vault dependencies not installed" in str(exc_info.value)
            assert "pip install azure-keyvault-secrets azure-identity" in str(
                exc_info.value
            )

    @patch("gen_epix.commondb.config.secret_provider.azure_key_vault.os.environ")
    def test_get_client_missing_vault_url(
        self, mock_environ: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test _get_client raises error when vault URL is not set."""
        mock_environ.get.side_effect = lambda key: None

        with pytest.raises(SecretLoadError) as exc_info:
            provider._get_client()

        assert (
            f"Environment variable {AzureKeyVaultSecretProvider.URL_ENV_VAR} not set"
            in str(exc_info.value)
        )

    @patch("gen_epix.commondb.config.secret_provider.azure_key_vault.os.environ")
    def test_get_client_with_client_secret_credentials(
        self, mock_environ: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test _get_client creates client with client secret credentials when all required env vars are set."""
        env_vars = {
            "AZURE_KEYVAULT_URL": "https://test-vault.vault.azure.net/",
            "AZURE_CLIENT_ID": "test-client-id",
            "AZURE_CLIENT_SECRET": "test-client-secret",
            "AZURE_TENANT_ID": "test-tenant-id",
        }
        mock_environ.get.side_effect = lambda key: env_vars.get(key)

        mock_credential = Mock()
        mock_client = Mock()

        # Mock the Azure imports since they happen inside the method
        with patch(
            "azure.identity.ClientSecretCredential", return_value=mock_credential
        ) as mock_client_secret_credential:
            with patch(
                "azure.keyvault.secrets.SecretClient", return_value=mock_client
            ) as mock_secret_client:
                result = provider._get_client()

                # Verify client secret credential was used
                mock_client_secret_credential.assert_called_once_with(
                    tenant_id="test-tenant-id",
                    client_id="test-client-id",
                    client_secret="test-client-secret",
                )

                # Verify SecretClient was created with correct parameters
                mock_secret_client.assert_called_once_with(
                    vault_url="https://test-vault.vault.azure.net/",
                    credential=mock_credential,
                )

                assert result == mock_client
                assert provider._client == mock_client

    @patch("gen_epix.commondb.config.secret_provider.azure_key_vault.os.environ")
    def test_get_client_with_default_credentials(
        self, mock_environ: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test _get_client creates client with default credentials when client secret credentials are incomplete."""
        env_vars = {
            "AZURE_KEYVAULT_URL": "https://test-vault.vault.azure.net/",
            "AZURE_CLIENT_ID": "test-client-id",
            # Missing AZURE_CLIENT_SECRET and AZURE_TENANT_ID
        }
        mock_environ.get.side_effect = lambda key: env_vars.get(key)

        mock_credential = Mock()
        mock_client = Mock()

        # Mock the Azure imports since they happen inside the method
        with patch(
            "azure.identity.DefaultAzureCredential", return_value=mock_credential
        ) as mock_default_credential:
            with patch(
                "azure.keyvault.secrets.SecretClient", return_value=mock_client
            ) as mock_secret_client:
                result = provider._get_client()

                # Verify default credential was used
                mock_default_credential.assert_called_once()

                # Verify SecretClient was created with correct parameters
                mock_secret_client.assert_called_once_with(
                    vault_url="https://test-vault.vault.azure.net/",
                    credential=mock_credential,
                )

                assert result == mock_client
                assert provider._client == mock_client

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_simple_secrets(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test loading simple string secrets from Azure Key Vault."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Mock secret properties
        secret_properties = [
            MockSecretProperty("TEST_database_host"),
            MockSecretProperty("TEST_database_port"),
            MockSecretProperty("OTHER_secret"),  # Should be ignored
            MockSecretProperty("test_api_key"),  # Case insensitive prefix matching
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        # Mock secret values
        secrets_data = {
            "TEST_database_host": MockSecret("TEST_database_host", "localhost"),
            "TEST_database_port": MockSecret("TEST_database_port", "5432"),
            "test_api_key": MockSecret("test_api_key", "secret123"),
        }
        mock_client.get_secret.side_effect = lambda name: secrets_data[name]

        secrets = provider.load_secrets()

        assert isinstance(secrets, DictProxy)
        # Keys are transformed: TEST_database_host -> database_host (prefix removed)
        assert secrets["database_host"] == "localhost"
        assert secrets["database_port"] == "5432"
        assert secrets["api_key"] == "secret123"

        # Verify the secrets are cached
        assert provider._secrets_cache is not None
        assert provider._secrets_cache is secrets

    def test_get_secret_success(self, provider: AzureKeyVaultSecretProvider) -> None:
        """Test get_secret returns correct value for existing key."""
        secrets = DictProxy({"api": {"key": "secret123"}})
        provider._secrets_cache = secrets

        result = provider.get_secret("api.key")
        assert result == "secret123"

    def test_get_secret_nonexistent_key(
        self, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test get_secret returns None for nonexistent key."""
        secrets = DictProxy({"api": {"key": "secret123"}})
        provider._secrets_cache = secrets

        result = provider.get_secret("nonexistent.key")
        assert result is None

    @patch.object(AzureKeyVaultSecretProvider, "load_secrets")
    def test_get_secret_loads_secrets_when_not_cached(
        self, mock_load_secrets: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test get_secret loads secrets when cache is empty."""
        secrets = DictProxy({"api": {"key": "secret123"}})
        mock_load_secrets.return_value = secrets

        # Simulate the load_secrets setting the cache
        def side_effect():
            provider._secrets_cache = secrets
            return secrets

        mock_load_secrets.side_effect = side_effect

        result = provider.get_secret("api.key")

        mock_load_secrets.assert_called_once()
        assert result == "secret123"

    def test_get_secret_handles_load_error(
        self, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test get_secret handles load errors gracefully."""
        with patch.object(
            provider, "load_secrets", side_effect=SecretLoadError("Load failed")
        ):
            result = provider.get_secret("api.key")
            assert result is None

    def test_get_secret_uses_cached_secrets(
        self, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test get_secret uses cached secrets and doesn't reload."""
        secrets = DictProxy({"api": {"key": "cached_value"}})
        provider._secrets_cache = secrets

        with patch.object(provider, "load_secrets") as mock_load:
            result = provider.get_secret("api.key")

            # Should not call load_secrets since cache exists
            mock_load.assert_not_called()
            assert result == "cached_value"

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_key_transformations(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test key name transformations (dashes, double dashes, case)."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        secret_properties = [
            MockSecretProperty("TEST_service_type"),  # underscore -> dot
            MockSecretProperty("TEST_database-host"),  # dash -> dot
            MockSecretProperty("TEST_API--KEY"),  # double dash -> underscore
            MockSecretProperty("TEST_Complex-Name--Test"),  # mixed transformations
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        secrets_data = {
            "TEST_service_type": MockSecret("TEST_service_type", "web"),
            "TEST_database-host": MockSecret("TEST_database-host", "localhost"),
            "TEST_API--KEY": MockSecret("TEST_API--KEY", "secret123"),
            "TEST_Complex-Name--Test": MockSecret("TEST_Complex-Name--Test", "value"),
        }
        mock_client.get_secret.side_effect = lambda name: secrets_data[name]

        secrets = provider.load_secrets()

        # Verify transformations (prefix removed, -- -> _, - -> ., lowercase applied)
        assert secrets["service_type"] == "web"
        assert secrets["database.host"] == "localhost"
        assert secrets["api_key"] == "secret123"
        assert secrets["complex.name_test"] == "value"

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_json_parsing(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test that JSON values are parsed correctly."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        secret_properties = [
            MockSecretProperty("TEST_config_database"),
            MockSecretProperty("TEST_features"),
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        secrets_data = {
            "TEST_config_database": MockSecret(
                "TEST_config_database", '{"host": "db.example.com", "port": 5432}'
            ),
            "TEST_features": MockSecret(
                "TEST_features", '["feature1", "feature2", "feature3"]'
            ),
        }
        mock_client.get_secret.side_effect = lambda name: secrets_data[name]

        with patch(
            "gen_epix.commondb.config.secret_provider.azure_key_vault.SettingsManager.parse_json"
        ) as mock_parse:
            mock_parse.side_effect = [
                {"host": "db.example.com", "port": 5432},
                ["feature1", "feature2", "feature3"],
            ]

            secrets = provider.load_secrets()

        assert secrets["config_database"]["host"] == "db.example.com"
        assert secrets["config_database"]["port"] == 5432
        assert secrets["features"] == ["feature1", "feature2", "feature3"]

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_prefix_filtering(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test that only secrets with correct prefix are loaded."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        secret_properties = [
            MockSecretProperty("TEST_valid_secret"),
            MockSecretProperty("OTHER_invalid_secret"),
            MockSecretProperty(
                "test_case_insensitive"
            ),  # Should match case-insensitively
            MockSecretProperty(
                "TESTING_partial_match"
            ),  # Should not match (different prefix)
            MockSecretProperty(None),  # Should handle None gracefully
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        secrets_data = {
            "TEST_valid_secret": MockSecret("TEST_valid_secret", "valid"),
            "test_case_insensitive": MockSecret("test_case_insensitive", "case_test"),
        }
        mock_client.get_secret.side_effect = lambda name: secrets_data.get(name, Mock())

        secrets = provider.load_secrets()

        # Only secrets with correct prefix should be loaded
        assert secrets["valid_secret"] == "valid"
        assert secrets["case_insensitive"] == "case_test"

        # Should not contain secrets with wrong prefix
        with pytest.raises(KeyError):
            _ = secrets["invalid_secret"]

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_error_handling(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test error handling during secret loading."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        secret_properties = [
            MockSecretProperty("TEST_good_secret"),
            MockSecretProperty("TEST_bad_secret"),
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        def mock_get_secret(name: str) -> MockSecret:
            if name == "TEST_bad_secret":
                raise Exception("Access denied")
            return MockSecret(name, "value")

        mock_client.get_secret.side_effect = mock_get_secret

        with patch("builtins.print") as mock_print:
            secrets = provider.load_secrets()

        # Should load good secrets and skip bad ones
        assert secrets["good_secret"] == "value"

        # Should not contain the failed secret
        with pytest.raises(KeyError):
            _ = secrets["bad_secret"]

        # Should have printed warning
        mock_print.assert_called()

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_empty_vault(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test load_secrets when no matching secrets are found."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # No secrets with correct prefix
        secret_properties = [
            MockSecretProperty("OTHER_secret1"),
            MockSecretProperty("DIFFERENT_secret2"),
        ]
        mock_client.list_properties_of_secrets.return_value = secret_properties

        # Since no secrets match the prefix, they should still be loaded as empty DictProxy
        secrets = provider.load_secrets()
        assert isinstance(secrets, DictProxy)
        # Should not contain secrets with wrong prefix
        with pytest.raises(KeyError):
            _ = secrets["secret1"]

    @patch.object(AzureKeyVaultSecretProvider, "_get_client")
    def test_load_secrets_list_failure(
        self, mock_get_client: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test load_secrets handles list_properties_of_secrets failure."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        mock_client.list_properties_of_secrets.side_effect = Exception(
            "Access denied to vault"
        )

        with pytest.raises(SecretLoadError) as exc_info:
            provider.load_secrets()

        assert "Failed to load secrets from Azure Key Vault" in str(exc_info.value)
        assert "Access denied to vault" in str(exc_info.value)

    def test_case_sensitivity_settings(self) -> None:
        """Test behavior with different case sensitivity settings."""
        # Test with case sensitivity enabled (default)
        provider_case_sensitive = AzureKeyVaultSecretProvider(
            prefix="TEST_", lowercase_keys=True
        )
        assert provider_case_sensitive.lowercase_keys is True

        # Test with case sensitivity disabled
        provider_case_insensitive = AzureKeyVaultSecretProvider(
            prefix="TEST_", lowercase_keys=False
        )
        assert provider_case_insensitive.lowercase_keys is False

    @patch("gen_epix.commondb.config.secret_provider.azure_key_vault.os.environ")
    def test_client_caching(
        self, mock_environ: Mock, provider: AzureKeyVaultSecretProvider
    ) -> None:
        """Test that Azure client is cached correctly."""
        # Setup environment variables properly (URL only, so DefaultAzureCredential is used)
        env_vars = {
            "AZURE_KEYVAULT_URL": "https://test-vault.vault.azure.net/",
        }
        mock_environ.get.side_effect = lambda key: env_vars.get(key)

        mock_credential = Mock()
        mock_client = Mock()

        with patch(
            "azure.identity.DefaultAzureCredential", return_value=mock_credential
        ) as mock_default_credential:
            with patch(
                "azure.keyvault.secrets.SecretClient", return_value=mock_client
            ) as mock_secret_client:
                # First call should create client
                result1 = provider._get_client()
                assert result1 == mock_client

                # Second call should return cached client
                result2 = provider._get_client()
                assert result2 == mock_client
                assert result1 is result2

                # Should only be called once due to caching
                mock_secret_client.assert_called_once()
                mock_default_credential.assert_called_once()
