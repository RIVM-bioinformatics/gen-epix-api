"""Adapters that expose a common field interface for row-like objects.

The adapters let transformers read, update, and inspect dictionaries, Pydantic
models, and Polars-like objects without depending on one concrete representation.
"""

from collections.abc import Hashable, Iterator
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class RowLike(Protocol):
    """Structural interface required by row-oriented transformation code."""

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Return the value for `key`, or `default` when the key is absent."""
        raise NotImplementedError()

    def __getitem__(self, key: Hashable) -> Any:
        """Return the value associated with `key`."""
        raise NotImplementedError()

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Set the value associated with `key`."""
        raise NotImplementedError()

    def __contains__(self, key: Hashable) -> bool:
        """Return whether `key` is present."""
        raise NotImplementedError()

    def keys(self) -> Iterator[Hashable]:
        """Iterate over the available keys."""
        raise NotImplementedError()


class DictAdapter:
    """Adapt a mutable dictionary to the transformer field interface."""

    def __init__(self, obj: dict):
        """Wrap a mutable mapping so transformers can read and update it."""
        self._obj = obj

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key with optional default."""
        return self._obj.get(key, default)

    def set(self, key: Hashable, value: Any) -> None:
        """Set value by key."""
        self._obj[key] = value

    def has_key(self, key: Hashable) -> bool:
        """Check if key exists."""
        return key in self._obj

    def keys(self) -> Iterator[Hashable]:
        """Get all keys."""
        return iter(self._obj.keys())


class PydanticAdapter:
    """Adapt a Pydantic model to the transformer field interface."""

    def __init__(self, obj: BaseModel):
        """Wrap a Pydantic model and expose fields through adapter methods."""
        self._obj = obj

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key with optional default."""
        return getattr(self._obj, str(key), default)

    def set(self, key: Hashable, value: Any) -> None:
        """Set value by key."""
        setattr(self._obj, str(key), value)

    def has_key(self, key: Hashable) -> bool:
        """Check if key exists."""
        return hasattr(self._obj, str(key))

    def keys(self) -> Iterator[Hashable]:
        """Get all keys."""
        return iter(self._obj.model_fields.keys())


class PolarsAdapter:
    """Adapt a Polars-like object with column access to the field interface."""

    def __init__(self, obj: Any):
        """Wrap a Polars-like object that exposes column access."""
        self._obj = obj

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key with optional default."""
        try:
            return self._obj[key]
        except (KeyError, IndexError):
            return default

    def set(self, key: Hashable, value: Any) -> None:
        """Set value by key."""
        self._obj = self._obj.with_columns({str(key): value})

    def has_key(self, key: Hashable) -> bool:
        """Check if key exists."""
        return str(key) in self._obj.columns

    def keys(self) -> Iterator[Hashable]:
        """Get all keys."""
        return iter(self._obj.columns)


class ObjectAdapter:
    """Select and delegate to an adapter for a supported object representation.

    Supported values are dictionaries, Pydantic models, and objects exposing a
    Polars-style `columns` attribute or dataframe protocol.

    Raises:
        ValueError: If `obj` does not match a supported representation.
    """

    def __init__(self, obj: dict | BaseModel | Any):
        """Select the concrete adapter for the wrapped object."""
        self._obj = obj
        self._adapter = self._create_adapter(obj)

    def _create_adapter(
        self, obj: Any
    ) -> DictAdapter | PydanticAdapter | PolarsAdapter:
        """Create the concrete adapter appropriate for `obj`."""
        if isinstance(obj, dict):
            return DictAdapter(obj)
        elif isinstance(obj, BaseModel):
            return PydanticAdapter(obj)
        elif hasattr(obj, "__dataframe__") or hasattr(
            obj, "columns"
        ):  # Polars detection
            return PolarsAdapter(obj)
        else:
            raise ValueError(f"Unsupported object type: {type(obj)}")

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key with optional default."""
        return self._adapter.get(key, default)

    def set(self, key: Hashable, value: Any) -> None:
        """Set value by key."""
        self._adapter.set(key, value)

    def has_key(self, key: Hashable) -> bool:
        """Check if key exists."""
        return self._adapter.has_key(key)

    def keys(self) -> Iterator[Hashable]:
        """Get all keys."""
        return self._adapter.keys()

    def unwrap(self) -> Any:
        """Return the wrapped object, including any adapter-applied updates."""
        return self._obj
