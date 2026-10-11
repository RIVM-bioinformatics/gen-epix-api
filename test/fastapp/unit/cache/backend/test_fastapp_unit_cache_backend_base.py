"""Exercise ordered batch defaults and the proxy delegation contract."""

from collections.abc import Iterator
from test.util.mock_compat import MagicMock

import pytest

from gen_epix.fastapp.cache.backend.base import CacheBackend, ProxyBackend
from gen_epix.fastapp.cache.lock import Mutex
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, EntryMetadata, NoValue
from gen_epix.fastapp.cache.stats import CacheStatistics


class _ConcreteBackend(CacheBackend):
    """Minimal store for exercising the base class's batch defaults."""

    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, CachedValue] = {}

    def get(self, key: str) -> CachedValue | NoValue:
        return self.values.get(key, NO_VALUE)

    def set(self, key: str, value: CachedValue) -> None:
        self.values[key] = value

    def delete(self, key: str) -> None:
        self.values.pop(key, None)

    def clear(self) -> None:
        self.values.clear()

    def contains(self, key: str) -> bool:
        return key in self.values

    def keys(self) -> Iterator[str]:
        return iter(self.values)


def _cached_value(payload: str) -> CachedValue:
    return CachedValue(payload, EntryMetadata(created_at=0.0))


def test_cache_backend_remains_abstract() -> None:
    """Reject direct instantiation of the abstract backend."""
    # This deliberate invalid construction verifies the abstract contract.
    # pylint: disable=abstract-class-instantiated
    with pytest.raises(TypeError):
        CacheBackend()


def test_default_multi_operations_preserve_order_and_ignore_missing_keys() -> None:
    """Preserve order and tolerate missing keys in the default batch methods."""
    backend = _ConcreteBackend()
    first = _cached_value("first")
    second = _cached_value("second")
    mapping = {"first": first, "second": second}

    CacheBackend.set_multi(backend, mapping)

    assert CacheBackend.get_multi(
        backend, iter(["second", "missing", "first", "second"])
    ) == [second, NO_VALUE, first, second]
    assert mapping == {"first": first, "second": second}
    assert CacheBackend.get_multi(backend, iter([])) == []

    CacheBackend.delete_multi(backend, iter(["first", "missing", "first"]))

    assert backend.values == {"second": second}
    CacheBackend.set_multi(backend, {})
    CacheBackend.delete_multi(backend, iter([]))
    assert backend.values == {"second": second}


def test_default_optional_hooks_return_empty_values_and_close_is_noop() -> None:
    """Return empty optional hooks and let the base close operation do nothing."""
    backend = _ConcreteBackend()

    assert CacheBackend.get_mutex(backend, "key") is None
    first = CacheBackend.statistics(backend)
    second = CacheBackend.statistics(backend)
    assert first == CacheStatistics()
    assert second == CacheStatistics()
    assert first is not second
    CacheBackend.close(backend)


def test_proxy_forwards_backend_operations() -> None:
    """Delegate every backend operation and return values unchanged."""
    backend = MagicMock(spec=CacheBackend)
    proxy = ProxyBackend(backend)
    value = _cached_value("payload")
    values = [value, NO_VALUE]
    mutex = MagicMock(spec=Mutex)
    statistics = CacheStatistics(hits=2)
    mapping = {"key": value}
    keys = ["key", "missing"]

    backend.get.return_value = value
    backend.contains.return_value = True
    backend.keys.return_value = iter(["key"])
    backend.get_multi.return_value = values
    backend.get_mutex.return_value = mutex
    backend.statistics.return_value = statistics

    assert proxy.get("key") is value
    proxy.set("key", value)
    proxy.delete("key")
    proxy.clear()
    assert proxy.contains("key") is True
    assert list(proxy.keys()) == ["key"]
    assert proxy.get_multi(keys) is values
    proxy.set_multi(mapping)
    proxy.delete_multi(keys)
    assert proxy.get_mutex("key") is mutex
    assert proxy.statistics() is statistics
    proxy.close()

    backend.get.assert_called_once_with("key")
    backend.set.assert_called_once_with("key", value)
    backend.delete.assert_called_once_with("key")
    backend.clear.assert_called_once_with()
    backend.contains.assert_called_once_with("key")
    backend.keys.assert_called_once_with()
    backend.get_multi.assert_called_once_with(keys)
    backend.set_multi.assert_called_once_with(mapping)
    backend.delete_multi.assert_called_once_with(keys)
    backend.get_mutex.assert_called_once_with("key")
    backend.statistics.assert_called_once_with()
    backend.close.assert_called_once_with()


def test_proxy_can_be_wrapped_later_and_propagates_backend_errors() -> None:
    """Allow late wrapping and propagate errors raised by the wrapped backend."""
    proxy = ProxyBackend(name="cache-proxy")

    with pytest.raises(RuntimeError, match="wraps nothing yet"):
        _ = proxy.proxied
    with pytest.raises(RuntimeError, match="wraps nothing yet"):
        proxy.get("key")

    backend = MagicMock(spec=CacheBackend)
    error = OSError("backend unavailable")
    backend.get.side_effect = error

    assert proxy.wrap(backend) is proxy
    assert proxy.name == "cache-proxy"
    assert proxy.proxied is backend
    with pytest.raises(OSError) as raised:
        proxy.get("key")
    assert raised.value is error
