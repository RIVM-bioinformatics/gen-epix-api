"""Cache store implementations.

The package exposes the abstract contract and the stores built on it:

- `CacheBackend` and `ProxyBackend` define and decorate the store contract.
- `MemoryBackend` is the default in-process store with capacity and expiry.
- `NullBackend` disables caching without changing any call site.
- `LayeredBackend` places a near tier in front of a shared tier.
- `RemovalListener` is the callback type reporting removals and their cause.
"""

from gen_epix.fastapp.cache.backend.base import CacheBackend, ProxyBackend
from gen_epix.fastapp.cache.backend.layered import LayeredBackend
from gen_epix.fastapp.cache.backend.memory import MemoryBackend, RemovalListener
from gen_epix.fastapp.cache.backend.null import NullBackend

__all__ = [
    "CacheBackend",
    "LayeredBackend",
    "MemoryBackend",
    "NullBackend",
    "ProxyBackend",
    "RemovalListener",
]
