from typing import Any, ItemsView, Iterator, KeysView, ValuesView


class DictProxy:
    """
    Proxy class to provide dict-like access with attribute notation.
    Only str keys are supported. If a key's value is a dict, it is wrapped in
    another DictProxy.
    If a key contains a double dash, it is treated as a single underscore. This
    is to support secret names that do not allow underscores.
    If a key contains dots or single dashes, it is treated as a nested key.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data: dict[str, Any] = {}
        if data:
            for key, value in data.items():
                DictProxy._set_value_recursion(self._data, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default."""
        key_parts = self._parse_key(key)
        data = self._data
        for key_part in key_parts:
            if key_part in data:
                data = data[key_part]
            else:
                return default
        return data

    def keys(self) -> KeysView[str]:
        """Return keys."""
        return self._data.keys()

    def values(self) -> ValuesView[Any]:
        """Return values."""
        return self._data.values()

    def items(self) -> ItemsView[str, Any]:
        """Return items."""
        return self._data.items()

    def update(self, other: dict[str, Any] | Any) -> None:
        for key, value in other.items():
            self._set_value(key, value)

    def _parse_key(self, key: str) -> list[str]:
        """Parse a key into parts, handling dots and dashes."""
        # Replace double dashes with single underscore
        key = key.replace("--", "_")
        # Split by dots or single dashes
        key_parts = []
        for key_part in key.split("."):
            key_parts.extend(key_part.split("-"))
        return key_parts

    def _set_value(self, key: str, value: Any) -> None:
        key_parts = self._parse_key(key)
        if len(key_parts) == 1:
            DictProxy._set_value_recursion(self._data, key, value)
            return
        data = self._data
        for key_part in key_parts[:-1]:
            if key_part not in data:
                data[key_part] = DictProxy()
            data = data[key_part]
        data[key_parts[-1]] = DictProxy()
        DictProxy._set_value_recursion(data, key_parts[-1], value)

    def _get_value(self, key: str, default: Any, raise_error: bool) -> Any:
        key_parts = self._parse_key(key)
        data = self._data
        for key_part in key_parts:
            if key_part not in data:
                if raise_error:
                    raise KeyError(f"Key '{key}' not found in DictProxy")
                return default
            data = data[key_part]
        return data

    def __getattr__(self, key: str) -> Any:
        """Support dot syntax."""
        if key.startswith("_"):
            return super().__getattribute__(key)
        try:
            return self._get_value(key, None, True)
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key: str, value: Any) -> None:
        """Support dot syntax."""
        if key.startswith("_"):
            return super().__setattr__(key, value)
        self._set_value(key, value)

    def __getitem__(self, key: str) -> Any:
        """Support [] syntax."""
        return self._get_value(key, None, True)

    def __setitem__(self, key: str, value: Any) -> None:
        """Support [] syntax."""
        self._set_value(key, value)

    def __contains__(self, key: str) -> bool:
        """Support 'in' syntax."""
        key_parts = self._parse_key(key)
        data = self._data
        for key_part in key_parts:
            if key_part not in data:
                return False
            data = data[key_part]
        return True

    def __iter__(self) -> Iterator[str]:  # pragma: no cover
        """Support iteration."""
        return iter(self._data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"

    @staticmethod
    def _set_value_recursion(data: Any, key: str, value: Any) -> None:
        if not isinstance(value, dict):
            # Not a dict, assign as is
            data[key] = value
            return
        if not all(isinstance(x, str) for x in value.keys()):
            # Not all keys are strings, assign as is
            data[key] = value
            return
        data[key] = DictProxy(data=value)
        for sub_key, sub_value in value.items():
            DictProxy._set_value_recursion(data[key], sub_key, sub_value)
