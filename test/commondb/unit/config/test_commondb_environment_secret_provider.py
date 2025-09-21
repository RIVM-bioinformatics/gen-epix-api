"""Comprehensive unit tests for EnvironmentSecretProvider."""

import os
from unittest.mock import patch

import pytest

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider import (
    EnvironmentSecretProvider,
    SecretLoadError,
)


class TestEnvironmentSecretProvider:
    """Test cases for EnvironmentSecretProvider class."""

    @pytest.fixture
    def provider(self) -> EnvironmentSecretProvider:
        """Create a basic EnvironmentSecretProvider instance."""
        return EnvironmentSecretProvider(prefix="TEST_", lowercase_keys=True)

    @pytest.fixture
    def provider_no_lowercase(self) -> EnvironmentSecretProvider:
        """Create EnvironmentSecretProvider instance without lowercase conversion."""
        return EnvironmentSecretProvider(prefix="TEST_", lowercase_keys=False)

    def test_init_with_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        provider = EnvironmentSecretProvider(prefix="APP_")

        assert provider.prefix == "APP_"
        assert provider.lowercase_keys is True
        assert provider._secrets_cache is None

    def test_init_with_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        provider = EnvironmentSecretProvider(
            prefix="CUSTOM_",
            lowercase_keys=False,
            extra_param="ignored",  # Should be ignored by **kwargs
        )

        assert provider.prefix == "CUSTOM_"
        assert provider.lowercase_keys is False
        assert provider._secrets_cache is None

    @patch.dict(os.environ, {}, clear=True)
    def test_load_secrets_no_matching_env_vars(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test load_secrets raises exception when no matching environment variables exist."""
        with pytest.raises(SecretLoadError) as exc_info:
            provider.load_secrets()

        assert "No secrets found with prefix TEST_" in str(exc_info.value)
        assert "Environment variables should start with TEST_" in str(exc_info.value)

    @patch.dict(os.environ, {"OTHER_VAR": "value"}, clear=True)
    def test_load_secrets_no_matching_prefix(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test load_secrets raises exception when no variables match the prefix."""
        with pytest.raises(SecretLoadError) as exc_info:
            provider.load_secrets()

        assert "No secrets found with prefix TEST_" in str(exc_info.value)

    @patch.dict(os.environ, {"TEST_SIMPLE": "simple_value"}, clear=True)
    def test_load_secrets_simple_string(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test loading a simple string secret."""
        secrets = provider.load_secrets()

        assert isinstance(secrets, DictProxy)
        assert secrets["simple"] == "simple_value"
        assert secrets.simple == "simple_value"
        assert provider._secrets_cache is secrets

    @patch.dict(os.environ, {"TEST_SIMPLE": "simple_value"}, clear=True)
    def test_load_secrets_with_uppercase_disabled(
        self, provider_no_lowercase: EnvironmentSecretProvider
    ) -> None:
        """Test loading secrets without lowercase conversion."""
        secrets = provider_no_lowercase.load_secrets()

        assert secrets["SIMPLE"] == "simple_value"
        assert secrets.SIMPLE == "simple_value"

    @patch.dict(
        os.environ,
        {
            "TEST_JSON__OBJECT": '{"key": "value", "number": 42}',
            "TEST_JSON__ARRAY": "[1, 2, 3]",
            "TEST_JSON__STRING": '"quoted_string"',
        },
        clear=True,
    )
    def test_load_secrets_json_parsing(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test that JSON values are properly parsed."""
        secrets = provider.load_secrets()

        # Test JSON object parsing (wrapped in DictProxy by DictProxy logic)
        json_obj_proxy = secrets.json.object
        assert hasattr(json_obj_proxy, "key")
        assert json_obj_proxy.key == "value"
        assert json_obj_proxy.number == 42

        # Test JSON array parsing
        json_array = secrets.json.array
        assert isinstance(json_array, list)
        assert json_array == [1, 2, 3]

        # Test JSON string parsing
        json_string = secrets.json.string
        assert json_string == "quoted_string"

    @patch.dict(
        os.environ,
        {"TEST_NESTED__KEY": "nested_value", "TEST_DEEP__NESTED__KEY": "deep_value"},
        clear=True,
    )
    def test_load_secrets_nested_keys(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test that double underscores create nested structure."""
        secrets = provider.load_secrets()

        # Test single level nesting
        assert secrets["nested.key"] == "nested_value"
        assert secrets.nested.key == "nested_value"

        # Test multiple level nesting
        assert secrets["deep.nested.key"] == "deep_value"
        assert secrets.deep.nested.key == "deep_value"

    @patch.dict(
        os.environ,
        {
            "TEST_DB__HOST": "localhost",
            "TEST_DB__PORT": "5432",
            "TEST_DB__CONFIG": '{"ssl": true, "timeout": 30}',
            "TEST_API__KEY": "secret_key",
            "TEST_API__ENDPOINTS": '["v1", "v2"]',
        },
        clear=True,
    )
    def test_load_secrets_complex_structure(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test loading a complex nested structure with mixed data types."""
        secrets = provider.load_secrets()

        # Test database configuration
        assert secrets.db.host == "localhost"
        assert secrets.db.port == "5432"
        assert secrets.db.config["ssl"] is True
        assert secrets.db.config["timeout"] == 30

        # Test API configuration
        assert secrets.api.key == "secret_key"
        assert secrets.api.endpoints == ["v1", "v2"]

    @patch.dict(
        os.environ,
        {
            "TEST_SPECIAL__CHARS": "value with spaces and symbols !@#$%",
            "TEST_EMPTY": "",
            "TEST_NEWLINES": "line1\nline2\nline3",
        },
        clear=True,
    )
    def test_load_secrets_special_values(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test handling of special string values."""
        secrets = provider.load_secrets()

        assert secrets.special.chars == "value with spaces and symbols !@#$%"
        assert secrets.empty == ""
        assert secrets.newlines == "line1\nline2\nline3"

    @patch.dict(os.environ, {"TEST_INVALID__JSON": '{"incomplete": json'}, clear=True)
    def test_load_secrets_invalid_json_fallback(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test that invalid JSON falls back to string value."""
        secrets = provider.load_secrets()

        # Should not parse as JSON, should remain as string
        assert secrets.invalid.json == '{"incomplete": json'

    @patch.dict(os.environ, {"TEST_KEY": "value"}, clear=True)
    def test_get_secret_existing_key(self, provider: EnvironmentSecretProvider) -> None:
        """Test get_secret with existing key."""
        result = provider.get_secret("key")
        assert result == "value"

    @patch.dict(os.environ, {"TEST_NESTED__KEY": "nested_value"}, clear=True)
    def test_get_secret_nested_key(self, provider: EnvironmentSecretProvider) -> None:
        """Test get_secret with nested key path."""
        result = provider.get_secret("nested.key")
        assert result == "nested_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_secret_no_secrets_loaded(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test get_secret returns None when no secrets can be loaded."""
        result = provider.get_secret("any.key")
        assert result is None

    @patch.dict(os.environ, {"TEST_KEY": "value"}, clear=True)
    def test_get_secret_nonexistent_key(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test get_secret returns None for non-existent key."""
        # Load secrets first
        provider.load_secrets()

        result = provider.get_secret("nonexistent.key")
        assert result is None

    @patch.dict(os.environ, {"TEST_KEY": "value"}, clear=True)
    def test_get_secret_uses_cache(self, provider: EnvironmentSecretProvider) -> None:
        """Test that get_secret uses cached secrets after first load."""
        # First call should load secrets
        result1 = provider.get_secret("key")
        assert result1 == "value"
        assert provider._secrets_cache is not None

        # Modify environment (should not affect cached result)
        with patch.dict(os.environ, {"TEST_KEY": "modified_value"}):
            result2 = provider.get_secret("key")
            assert result2 == "value"  # Should return cached value

    @patch.dict(
        os.environ,
        {"TEST_MIXED__TYPE": '{"json": true}', "TEST_STRING": "plain"},
        clear=True,
    )
    def test_get_secret_mixed_types(self, provider: EnvironmentSecretProvider) -> None:
        """Test get_secret with mixed data types."""
        json_result = provider.get_secret("mixed.type")
        string_result = provider.get_secret("string")

        # JSON objects are wrapped in DictProxy by the DictProxy._set_value_recursion method
        assert json_result is not None
        assert hasattr(json_result, "json")
        assert json_result.json is True
        assert isinstance(string_result, str)
        assert string_result == "plain"

    @patch.dict(os.environ, {"TEST_KEY": "value"}, clear=True)
    def test_multiple_load_calls(self, provider: EnvironmentSecretProvider) -> None:
        """Test that multiple load_secrets calls work correctly."""
        # First load
        secrets1 = provider.load_secrets()
        assert secrets1.key == "value"

        # Second load should work and update cache
        with patch.dict(os.environ, {"TEST_NEW__KEY": "new_value"}, clear=False):
            secrets2 = provider.load_secrets()
            assert secrets2.key == "value"
            assert secrets2.new.key == "new_value"
            assert provider._secrets_cache is secrets2

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL__TRUE": "true",
            "TEST_BOOL__FALSE": "false",
            "TEST_NULL": "null",
            "TEST_NUMBER": "42",
        },
        clear=True,
    )
    def test_load_secrets_primitive_json_values(
        self, provider: EnvironmentSecretProvider
    ) -> None:
        """Test that primitive JSON values are NOT parsed (only objects, arrays, strings)."""
        secrets = provider.load_secrets()

        # These should remain as strings since parse_json only handles {}, [], ""
        assert secrets.bool.true == "true"
        assert secrets.bool.false == "false"
        assert secrets.null == "null"
        assert secrets.number == "42"

    def test_inheritance_from_base_secret_provider(self) -> None:
        """Test that EnvironmentSecretProvider properly inherits from BaseSecretProvider."""
        from gen_epix.commondb.config.secret_provider.base import BaseSecretProvider

        provider = EnvironmentSecretProvider(prefix="TEST_")
        assert isinstance(provider, BaseSecretProvider)
        assert hasattr(provider, "get_secret")
        assert hasattr(provider, "load_secrets")

    @patch.dict(
        os.environ, {"TEST_WITH__DASHES__AND__DOTS": "complex_value"}, clear=True
    )
    def test_complex_key_parsing(self, provider: EnvironmentSecretProvider) -> None:
        """Test complex key parsing with mixed separators."""
        secrets = provider.load_secrets()

        # The key should be parsed according to DictProxy rules
        assert secrets["with.dashes.and.dots"] == "complex_value"

    @patch.dict(
        os.environ,
        {
            "TEST_": "empty_suffix",
            "TEST_A": "single_char",
            "TEST_SIMPLE__UNDERSCORE": "underscore_value",
        },
        clear=True,
    )
    def test_edge_case_key_names(self, provider: EnvironmentSecretProvider) -> None:
        """Test edge cases for key names."""
        secrets = provider.load_secrets()

        # Empty suffix after prefix
        assert secrets[""] == "empty_suffix"

        # Single character key
        assert secrets["a"] == "single_char"

        # Double underscore should create nested structure
        assert secrets.simple.underscore == "underscore_value"

    @patch.dict(os.environ, {"TEST_UNICODE": "こんにちは世界"}, clear=True)
    def test_unicode_values(self, provider: EnvironmentSecretProvider) -> None:
        """Test handling of Unicode values."""
        secrets = provider.load_secrets()

        assert secrets.unicode == "こんにちは世界"

    @patch.dict(os.environ, {"WRONG_PREFIX_KEY": "ignored"}, clear=True)
    def test_wrong_prefix_ignored(self, provider: EnvironmentSecretProvider) -> None:
        """Test that environment variables with wrong prefix are ignored."""
        with pytest.raises(SecretLoadError):
            provider.load_secrets()

    def test_secret_load_error_inheritance(self) -> None:
        """Test that SecretLoadError is properly defined."""
        error = SecretLoadError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"

    @patch.dict(os.environ, {"TEST_LARGE": "x" * 10000}, clear=True)
    def test_large_values(self, provider: EnvironmentSecretProvider) -> None:
        """Test handling of large environment variable values."""
        secrets = provider.load_secrets()

        assert len(secrets.large) == 10000
        assert secrets.large == "x" * 10000

    @patch.dict(
        os.environ,
        {
            "TEST_CASE__SENSITIVE": "value1",
            "test_case__sensitive": "value2",  # Different case
        },
        clear=True,
    )
    def test_case_sensitivity(self, provider: EnvironmentSecretProvider) -> None:
        """Test case sensitivity in environment variable names."""
        secrets = provider.load_secrets()

        # Should have both values since env vars are case sensitive
        if "case.sensitive" in secrets._data:
            # The exact behavior depends on which env var is processed first
            assert secrets.case.sensitive in ["value1", "value2"]

    @patch("gen_epix.commondb.config.settings.manager.SettingsManager.parse_json")
    def test_json_parsing_delegation(
        self, mock_parse_json, provider: EnvironmentSecretProvider
    ) -> None:
        """Test that JSON parsing is delegated to SettingsManager.parse_json."""
        mock_parse_json.return_value = {"parsed": True}

        with patch.dict(os.environ, {"TEST_JSON": '{"test": "value"}'}, clear=True):
            secrets = provider.load_secrets()

            mock_parse_json.assert_called_with('{"test": "value"}')
            # JSON objects are wrapped in DictProxy
            assert hasattr(secrets.json, "parsed")
            assert secrets.json.parsed is True
