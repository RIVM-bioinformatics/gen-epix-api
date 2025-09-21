"""Test DictProxy functionality."""

from typing import Any, Dict

import pytest

from gen_epix.commondb.config.dict_proxy import DictProxy


class TestDictProxy:
    """Test cases for DictProxy class."""

    def test_dictproxy_basic_access(self) -> None:
        """Test basic attribute and item access."""
        test_data = {
            "existing_key": "existing_value",
            "nested": {"inner_key": "inner_value"},
        }

        proxy = DictProxy(data=test_data)

        # Test attribute access
        assert proxy.existing_key == "existing_value"
        assert proxy.nested.inner_key == "inner_value"

        # Test item access
        assert proxy["existing_key"] == "existing_value"
        assert proxy["nested"]["inner_key"] == "inner_value"

    def test_dictproxy_item_assignment(self) -> None:
        """Test DictProxy item assignment functionality."""
        test_data: Dict[str, Any] = {
            "existing_key": "existing_value",
            "nested": {"inner_key": "inner_value"},
        }

        proxy = DictProxy(data=test_data)

        # Test item assignment
        proxy["new_key"] = "new_value"
        assert proxy.new_key == "new_value"
        assert proxy["new_key"] == "new_value"

        # Test that original data is NOT modified (DictProxy copies the data)
        assert "new_key" not in test_data

    def test_dictproxy_attribute_assignment(self) -> None:
        """Test DictProxy attribute assignment functionality."""
        test_data: Dict[str, Any] = {"existing_key": "existing_value"}

        proxy = DictProxy(data=test_data)

        # Test attribute assignment
        proxy.attr_key = "attr_value"
        assert proxy.attr_key == "attr_value"
        assert proxy["attr_key"] == "attr_value"

        # Test that original data is NOT modified (DictProxy copies the data)
        assert "attr_key" not in test_data

    def test_dictproxy_modify_existing_key(self) -> None:
        """Test modifying existing keys via assignment."""
        test_data: Dict[str, Any] = {"existing_key": "existing_value"}

        proxy = DictProxy(data=test_data)

        # Test modifying existing key via item assignment
        proxy["existing_key"] = "modified_value"
        assert proxy.existing_key == "modified_value"
        # Original data should NOT be modified (DictProxy copies the data)
        assert test_data["existing_key"] == "existing_value"

        # Test modifying existing key via attribute assignment
        proxy.existing_key = "attr_modified_value"
        assert proxy["existing_key"] == "attr_modified_value"
        # Original data should still be unchanged
        assert test_data["existing_key"] == "existing_value"

    def test_dictproxy_nested_structure_assignment(self) -> None:
        """Test adding nested structure via assignment."""
        test_data: Dict[str, Any] = {}

        proxy = DictProxy(data=test_data)

        # Test adding nested structure
        proxy["new_nested"] = {"deep": {"value": "deep_value"}}
        assert proxy.new_nested.deep.value == "deep_value"
        # Original data should NOT be modified (DictProxy copies the data)
        assert "new_nested" not in test_data

    def test_dictproxy_get_method(self) -> None:
        """Test DictProxy get method with defaults."""
        test_data: Dict[str, Any] = {"existing_key": "existing_value"}

        proxy = DictProxy(data=test_data)

        # Test get with existing key
        assert proxy.get("existing_key") == "existing_value"

        # Test get with non-existing key and default
        assert proxy.get("non_existing_key", "default_value") == "default_value"

        # Test get with non-existing key and no default
        assert proxy.get("non_existing_key") is None

    def test_dictproxy_nested_proxy_behavior(self) -> None:
        """Test that nested dictionaries are also wrapped in DictProxy."""
        test_data: Dict[str, Any] = {
            "nested": {
                "inner_key": "inner_value",
                "deep_nested": {"deep_key": "deep_value"},
            }
        }

        proxy = DictProxy(data=test_data)

        # Test that nested access returns DictProxy instances
        nested_proxy = proxy.nested
        assert isinstance(nested_proxy, DictProxy)
        assert nested_proxy.inner_key == "inner_value"

        # Test assignment to nested proxy
        nested_proxy.new_inner_key = "new_inner_value"
        assert proxy.nested.new_inner_key == "new_inner_value"
        # Original data should NOT be modified (DictProxy copies the data)
        assert "new_inner_key" not in test_data["nested"]

    def test_dictproxy_private_attributes(self) -> None:
        """Test that private attributes (starting with _) work correctly."""
        test_data: Dict[str, Any] = {"key": "value"}

        proxy = DictProxy(data=test_data)

        # Test that _data attribute is accessible and contains same content but is not the same object
        assert proxy._data is not test_data  # Different objects
        assert proxy._data == test_data  # Same content

        # Test that setting private attributes doesn't affect data
        proxy._test_attr = "test_value"
        assert proxy._test_attr == "test_value"
        assert "_test_attr" not in test_data
        assert "_test_attr" not in proxy._data

    def test_dictproxy_keyerror_handling(self) -> None:
        """Test proper error handling for missing keys."""
        test_data: Dict[str, Any] = {"existing_key": "value"}

        proxy = DictProxy(data=test_data)

        # Test KeyError for item access
        with pytest.raises(KeyError):
            _ = proxy["non_existing_key"]

        # Test AttributeError for attribute access
        with pytest.raises(AttributeError):
            _ = proxy.non_existing_key

    def test_dictproxy_keys_method(self) -> None:
        """Test DictProxy keys() method."""
        test_data: Dict[str, Any] = {
            "key1": "value1",
            "key2": "value2",
            "nested": {"inner": "value"},
        }

        proxy = DictProxy(data=test_data)
        keys = proxy.keys()

        # Test that keys() returns the same keys as the original dict
        assert set(keys) == set(test_data.keys())
        assert "key1" in keys
        assert "key2" in keys
        assert "nested" in keys
        assert "non_existing" not in keys

    def test_dictproxy_values_method(self) -> None:
        """Test DictProxy values() method."""
        test_data: Dict[str, Any] = {
            "simple": "simple_value",
            "number": 42,
            "nested": {"inner": "inner_value"},
        }

        proxy = DictProxy(data=test_data)
        values = list(proxy.values())

        # Test that we have the right number of values
        assert len(values) == 3

        # Test that simple values are returned as-is
        assert "simple_value" in values
        assert 42 in values

        # Test that nested dicts are wrapped in DictProxy
        nested_proxy = None
        for value in values:
            if hasattr(value, "inner"):
                nested_proxy = value
                break

        assert nested_proxy is not None
        assert isinstance(nested_proxy, DictProxy)
        assert nested_proxy.inner == "inner_value"

    def test_dictproxy_contains_method(self) -> None:
        """Test DictProxy __contains__ method (in operator)."""
        test_data: Dict[str, Any] = {
            "existing_key": "value",
            "nested": {"inner_key": "inner_value"},
            "number": 42,
        }

        proxy = DictProxy(data=test_data)

        # Test that existing keys are found
        assert "existing_key" in proxy
        assert "nested" in proxy
        assert "number" in proxy

        # Test that non-existing keys are not found
        assert "non_existing_key" not in proxy
        assert "missing" not in proxy

        # Test that nested keys are not directly accessible via contains
        assert "inner_key" not in proxy  # This is in nested, not in proxy directly

    def test_dictproxy_dict_like_behavior(self) -> None:
        """Test that DictProxy behaves like a dict for common operations."""
        test_data: Dict[str, Any] = {
            "key1": "value1",
            "key2": {"nested": "nested_value"},
            "key3": 123,
        }

        proxy = DictProxy(data=test_data)

        # Test iteration over keys
        collected_keys = []
        for key in proxy.keys():
            collected_keys.append(key)
        assert set(collected_keys) == {"key1", "key2", "key3"}

        # Test iteration over values
        collected_values = []
        for value in proxy.values():
            if isinstance(value, DictProxy):
                collected_values.append(value.nested)
            else:
                collected_values.append(value)
        assert set(collected_values) == {"value1", "nested_value", 123}

        # Test membership testing
        assert "key1" in proxy
        assert "key2" in proxy
        assert "key3" in proxy
        assert "nonexistent" not in proxy
