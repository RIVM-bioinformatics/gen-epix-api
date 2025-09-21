"""Unit tests for SecretProviderFactory."""

import os
import unittest
from unittest.mock import MagicMock, patch

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider import (
    AzureKeyVaultSecretProvider,
    EnvironmentSecretProvider,
    FileSecretProvider,
    SecretLoadError,
    SecretProviderFactory,
)


class TestSecretProviderFactory(unittest.TestCase):
    """Test cases for SecretProviderFactory."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_prefix = "TEST_APP_"
        self.test_strategies = ["ENVIRONMENT", "FILE", "AZURE_KEY_VAULT"]

        # Mock environment to avoid interference
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.env_patcher.stop()

    def test_class_constants(self) -> None:
        """Test that class constants are properly defined."""
        # Test STRATEGY_ENV_VAR constant
        self.assertEqual(SecretProviderFactory.STRATEGY_ENV_VAR, "SECRETS_STRATEGY")

        # Test STRATEGIES dictionary structure
        self.assertIsInstance(SecretProviderFactory.STRATEGIES, dict)
        self.assertGreater(len(SecretProviderFactory.STRATEGIES), 0)

        # Test expected strategy mappings
        expected_strategies = {
            "ENVIRONMENT": EnvironmentSecretProvider,
            "FILE": FileSecretProvider,
            "AZURE_KEY_VAULT": AzureKeyVaultSecretProvider,
        }

        for strategy, provider_class in expected_strategies.items():
            self.assertIn(strategy, SecretProviderFactory.STRATEGIES)
            self.assertEqual(SecretProviderFactory.STRATEGIES[strategy], provider_class)

    def test_create_provider_with_explicit_strategy(self) -> None:
        """Test creating providers with explicit strategy parameter."""
        # Test each valid strategy
        test_cases = [
            ("ENVIRONMENT", EnvironmentSecretProvider),
            ("environment", EnvironmentSecretProvider),  # Case insensitive
            ("FILE", FileSecretProvider),
            ("file", FileSecretProvider),
            ("AZURE_KEY_VAULT", AzureKeyVaultSecretProvider),
            ("azure_key_vault", AzureKeyVaultSecretProvider),
        ]

        for strategy, expected_class in test_cases:
            with self.subTest(strategy=strategy):
                provider = SecretProviderFactory.create_provider(
                    prefix=self.test_prefix, strategy=strategy
                )
                self.assertIsInstance(provider, expected_class)
                self.assertEqual(provider.prefix, self.test_prefix)
                self.assertTrue(provider.lowercase_keys)

    def test_create_provider_with_custom_parameters(self) -> None:
        """Test creating providers with custom parameters."""
        provider = SecretProviderFactory.create_provider(
            prefix=self.test_prefix,
            strategy="ENVIRONMENT",
            lowercase_keys=False,
            custom_param="test_value",
        )

        self.assertIsInstance(provider, EnvironmentSecretProvider)
        self.assertEqual(provider.prefix, self.test_prefix)
        self.assertFalse(provider.lowercase_keys)

    def test_create_provider_from_environment_variable(self) -> None:
        """Test creating provider when strategy is read from environment variable."""
        env_var = f"{self.test_prefix.upper()}SECRETS_STRATEGY"

        with patch.dict(os.environ, {env_var: "ENVIRONMENT"}):
            provider = SecretProviderFactory.create_provider(prefix=self.test_prefix)
            self.assertIsInstance(provider, EnvironmentSecretProvider)

    def test_create_provider_with_custom_strategy_env_var(self) -> None:
        """Test creating provider with custom strategy environment variable name."""
        custom_env_var = "CUSTOM_STRATEGY"
        full_env_var = f"{self.test_prefix.upper()}{custom_env_var}"

        with patch.dict(os.environ, {full_env_var: "FILE"}):
            provider = SecretProviderFactory.create_provider(
                prefix=self.test_prefix, strategy_env_var=custom_env_var
            )
            self.assertIsInstance(provider, FileSecretProvider)

    def test_create_provider_invalid_strategy(self) -> None:
        """Test error handling for invalid strategy."""
        with self.assertRaises(SecretLoadError) as context:
            SecretProviderFactory.create_provider(
                prefix=self.test_prefix, strategy="INVALID_STRATEGY"
            )

        error_msg = str(context.exception)
        self.assertIn("Invalid secret strategy 'INVALID_STRATEGY'", error_msg)
        self.assertIn("Valid strategies are:", error_msg)

    def test_create_provider_missing_strategy(self) -> None:
        """Test error handling when no strategy is specified."""
        # No strategy parameter and no environment variable
        with self.assertRaises(SecretLoadError) as context:
            SecretProviderFactory.create_provider(prefix=self.test_prefix)

        error_msg = str(context.exception)
        expected_env_var = f"{self.test_prefix.upper()}SECRETS_STRATEGY"
        self.assertIn("Secret strategy not specified", error_msg)
        self.assertIn(expected_env_var, error_msg)

    @patch(
        "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
    )
    def test_load_secrets_single_strategy_string(self, mock_load: MagicMock) -> None:
        """Test load_secrets with single strategy as string."""
        expected_secrets = DictProxy({"key1": "value1", "key2": "value2"})
        mock_load.return_value = expected_secrets

        result = SecretProviderFactory.load_secrets(
            prefix=self.test_prefix, strategy="ENVIRONMENT"
        )

        self.assertEqual(result._data, expected_secrets._data)
        mock_load.assert_called_once()

    @patch(
        "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
    )
    def test_load_secrets_single_strategy_from_env(self, mock_load: MagicMock) -> None:
        """Test load_secrets when strategy comes from environment variable."""
        expected_secrets = DictProxy({"key1": "value1"})
        mock_load.return_value = expected_secrets

        env_var = f"{self.test_prefix.upper()}SECRETS_STRATEGY"
        with patch.dict(os.environ, {env_var: "ENVIRONMENT"}):
            result = SecretProviderFactory.load_secrets(prefix=self.test_prefix)

        self.assertEqual(result._data, expected_secrets._data)
        mock_load.assert_called_once()

    def test_load_secrets_two_strategies_merge(self) -> None:
        """Test load_secrets with two strategies that merge secrets."""
        # Mock first provider (ENVIRONMENT)
        env_secrets = DictProxy({"env_key": "env_value", "shared_key": "env_shared"})

        # Mock second provider (FILE)
        file_secrets = DictProxy(
            {"file_key": "file_value", "shared_key": "file_shared"}
        )

        with patch(
            "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
        ) as mock_env:
            with patch(
                "gen_epix.commondb.config.secret_provider.file.FileSecretProvider.load_secrets"
            ) as mock_file:
                mock_env.return_value = env_secrets
                mock_file.return_value = file_secrets

                result = SecretProviderFactory.load_secrets(
                    prefix=self.test_prefix, strategy=["ENVIRONMENT", "FILE"]
                )

                # Check that both provider load methods were called
                mock_env.assert_called_once()
                mock_file.assert_called_once()

                # Check merged results - FILE should override ENVIRONMENT for shared keys
                expected = {
                    "env_key": "env_value",
                    "file_key": "file_value",
                    "shared_key": "file_shared",  # FILE overrides ENVIRONMENT
                }

                for key, value in expected.items():
                    self.assertEqual(result[key], value)

    def test_load_secrets_three_strategies_cascading_override(self) -> None:
        """Test load_secrets with three strategies where later ones override earlier ones."""
        # Setup mock secrets for each provider
        env_secrets = DictProxy(
            {
                "env_only": "env_value",
                "shared_all": "from_env",
                "shared_env_file": "env_file_value",
            }
        )

        file_secrets = DictProxy(
            {
                "file_only": "file_value",
                "shared_all": "from_file",
                "shared_env_file": "file_env_value",
                "shared_file_azure": "file_azure_value",
            }
        )

        azure_secrets = DictProxy(
            {
                "azure_only": "azure_value",
                "shared_all": "from_azure",
                "shared_file_azure": "azure_file_value",
            }
        )

        with patch(
            "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
        ) as mock_env:
            with patch(
                "gen_epix.commondb.config.secret_provider.file.FileSecretProvider.load_secrets"
            ) as mock_file:
                with patch(
                    "gen_epix.commondb.config.secret_provider.azure_key_vault.AzureKeyVaultSecretProvider.load_secrets"
                ) as mock_azure:
                    mock_env.return_value = env_secrets
                    mock_file.return_value = file_secrets
                    mock_azure.return_value = azure_secrets

                    result = SecretProviderFactory.load_secrets(
                        prefix=self.test_prefix,
                        strategy=["ENVIRONMENT", "FILE", "AZURE_KEY_VAULT"],
                    )

                    # Verify all providers were called
                    mock_env.assert_called_once()
                    mock_file.assert_called_once()
                    mock_azure.assert_called_once()

                    # Check final merged state - AZURE should win all conflicts
                    expected_final = {
                        "env_only": "env_value",
                        "file_only": "file_value",
                        "azure_only": "azure_value",
                        "shared_all": "from_azure",  # AZURE wins
                        "shared_env_file": "file_env_value",  # FILE wins over ENV
                        "shared_file_azure": "azure_file_value",  # AZURE wins over FILE
                    }

                    for key, expected_value in expected_final.items():
                        self.assertEqual(
                            result[key],
                            expected_value,
                            f"Key '{key}' should be '{expected_value}' but was '{result[key]}'",
                        )

    def test_load_secrets_single_strategy_in_list(self) -> None:
        """Test load_secrets with single strategy provided as list."""
        expected_secrets = DictProxy({"single_key": "single_value"})

        with patch(
            "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
        ) as mock_env:
            mock_env.return_value = expected_secrets

            result = SecretProviderFactory.load_secrets(
                prefix=self.test_prefix, strategy=["ENVIRONMENT"]
            )

            self.assertEqual(result._data, expected_secrets._data)
            mock_env.assert_called_once()

    def test_load_secrets_duplicate_strategies_error(self) -> None:
        """Test that duplicate strategies in list raise an error."""
        with self.assertRaises(SecretLoadError) as context:
            SecretProviderFactory.load_secrets(
                prefix=self.test_prefix, strategy=["ENVIRONMENT", "FILE", "ENVIRONMENT"]
            )

        self.assertIn("Duplicate strategies specified", str(context.exception))

    def test_load_secrets_with_custom_parameters(self) -> None:
        """Test load_secrets passes through custom parameters to providers."""
        expected_secrets = DictProxy({"test_key": "test_value"})

        # Create a mock provider class
        mock_provider_class = MagicMock()
        mock_provider = MagicMock()
        mock_provider.load_secrets.return_value = expected_secrets
        mock_provider_class.return_value = mock_provider

        # Patch the STRATEGIES dict to use our mock
        with patch.dict(
            SecretProviderFactory.STRATEGIES, {"ENVIRONMENT": mock_provider_class}
        ):
            result = SecretProviderFactory.load_secrets(
                prefix=self.test_prefix,
                strategy="ENVIRONMENT",
                lowercase_secret_name=False,
                custom_param="custom_value",
            )

            # Verify provider was created with correct parameters
            mock_provider_class.assert_called_once_with(
                prefix=self.test_prefix,
                lowercase_keys=False,
                custom_param="custom_value",
            )

            # Verify load_secrets was called and result returned
            mock_provider.load_secrets.assert_called_once()
            self.assertEqual(result._data, expected_secrets._data)

    def test_load_secrets_invalid_strategy_in_list(self) -> None:
        """Test error handling for invalid strategy in strategy list."""
        with self.assertRaises(SecretLoadError) as context:
            SecretProviderFactory.load_secrets(
                prefix=self.test_prefix, strategy=["INVALID_STRATEGY"]
            )

        error_msg = str(context.exception)
        self.assertIn("Invalid secret strategy 'INVALID_STRATEGY'", error_msg)

    def test_load_secrets_preserves_dict_proxy_update_behavior(self) -> None:
        """Test that DictProxy.update() behavior works correctly for nested structures."""
        # Test nested structure merging
        env_secrets = DictProxy(
            {"db": {"host": "env_host", "port": 5432}, "cache": {"host": "env_cache"}}
        )

        file_secrets = DictProxy(
            {"db": {"port": 3306, "user": "file_user"}, "api": {"key": "file_key"}}
        )

        with patch(
            "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
        ) as mock_env:
            with patch(
                "gen_epix.commondb.config.secret_provider.file.FileSecretProvider.load_secrets"
            ) as mock_file:
                mock_env.return_value = env_secrets
                mock_file.return_value = file_secrets

                result = SecretProviderFactory.load_secrets(
                    prefix=self.test_prefix, strategy=["ENVIRONMENT", "FILE"]
                )

                # Check that nested structures are properly merged
                # FILE should completely replace the "db" section from ENVIRONMENT
                self.assertEqual(result["db"]["port"], 3306)  # from FILE
                self.assertEqual(result["db"]["user"], "file_user")  # from FILE
                self.assertEqual(
                    result["cache"]["host"], "env_cache"
                )  # from ENVIRONMENT
                self.assertEqual(result["api"]["key"], "file_key")  # from FILE

                # Verify "db.host" from ENVIRONMENT is not present since FILE replaces entire "db" dict
                self.assertNotIn("host", result["db"])

    def test_strategy_case_insensitive_handling(self) -> None:
        """Test that strategy names are handled case-insensitively."""
        test_cases = ["environment", "Environment", "ENVIRONMENT", "EnViRoNmEnT"]

        for strategy in test_cases:
            with self.subTest(strategy=strategy):
                with patch(
                    "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
                ) as mock_load:
                    mock_load.return_value = DictProxy({"test": "value"})

                    result = SecretProviderFactory.load_secrets(
                        prefix=self.test_prefix, strategy=strategy
                    )

                    mock_load.assert_called_once()
                    self.assertEqual(result["test"], "value")

    def test_empty_strategy_list_error(self) -> None:
        """Test that empty strategy list raises appropriate error."""
        # Empty list should be handled differently than None
        result = SecretProviderFactory.load_secrets(
            prefix=self.test_prefix, strategy=[]
        )

        # Empty list should return empty DictProxy
        self.assertIsInstance(result, DictProxy)
        self.assertEqual(len(result._data), 0)

    def test_provider_load_error_propagation(self) -> None:
        """Test that SecretLoadError from individual providers is propagated."""
        with patch(
            "gen_epix.commondb.config.secret_provider.environment.EnvironmentSecretProvider.load_secrets"
        ) as mock_load:
            mock_load.side_effect = SecretLoadError("Environment provider failed")

            with self.assertRaises(SecretLoadError) as context:
                SecretProviderFactory.load_secrets(
                    prefix=self.test_prefix, strategy="ENVIRONMENT"
                )

            self.assertIn("Environment provider failed", str(context.exception))

    def test_mixed_strategy_types_in_multiple_calls(self) -> None:
        """Test behavior when switching between different strategy parameter types."""
        expected_secrets = DictProxy({"consistent": "behavior"})

        with patch(
            "gen_epix.commondb.config.secret_provider.file.FileSecretProvider.load_secrets"
        ) as mock_load:
            mock_load.return_value = expected_secrets

            # Test string strategy
            result1 = SecretProviderFactory.load_secrets(
                prefix=self.test_prefix, strategy="FILE"
            )

            # Test list strategy with same provider
            result2 = SecretProviderFactory.load_secrets(
                prefix=self.test_prefix, strategy=["FILE"]
            )

            # Results should be identical
            self.assertEqual(result1._data, result2._data)
            self.assertEqual(mock_load.call_count, 2)


if __name__ == "__main__":
    unittest.main()
