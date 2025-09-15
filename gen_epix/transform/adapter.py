"""
Object adapters for providing unified interface across different object types.
"""

from collections.abc import Hashable
from typing import Any, Iterator, Protocol, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class RowLike(Protocol):
    """Protocol for row-like objects."""

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key with optional default."""
        ...

    def __getitem__(self, key: Hashable) -> Any:
        """Get value by key."""
        ...

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Set value by key."""
        ...

    def __contains__(self, key: Hashable) -> bool:
        """Check if key exists."""
        ...

    def keys(self) -> Iterator[Hashable]:
        """Get all keys."""
        ...


class DictAdapter:
    """Adapter for dictionary objects."""

    def __init__(self, obj: dict):
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
    """Adapter for Pydantic model objects."""

    def __init__(self, obj: BaseModel):
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
    """Adapter for Polars objects."""

    def __init__(self, obj: Any):
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
    """
    Unified adapter that provides consistent interface for different object types.

    Supports dict, Pydantic models, and Polars objects.
    """

    def __init__(self, obj: dict | BaseModel | Any):
        self._obj = obj
        self._adapter = self._create_adapter(obj)

    def _create_adapter(
        self, obj: Any
    ) -> DictAdapter | PydanticAdapter | PolarsAdapter:
        """Factory method to create appropriate adapter for object type."""
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
        """Return the original object."""
        return self._obj
