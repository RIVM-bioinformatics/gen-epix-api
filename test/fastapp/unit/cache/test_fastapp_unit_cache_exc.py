import pytest

from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheConfigurationError,
    CacheError,
    CacheTimeoutError,
    CantDeserializeError,
    CircuitOpenError,
    KeyRejectedError,
    RegionAlreadyConfiguredError,
    RegionNotConfiguredError,
    RegionNotFoundError,
    SerializationError,
)


@pytest.mark.parametrize(
    ("error_type", "parent_type"),
    [
        (CacheError, Exception),
        (CacheConfigurationError, CacheError),
        (RegionAlreadyConfiguredError, CacheConfigurationError),
        (RegionNotConfiguredError, CacheConfigurationError),
        (RegionNotFoundError, CacheConfigurationError),
        (CacheBackendError, CacheError),
        (CacheTimeoutError, CacheBackendError),
        (CircuitOpenError, CacheBackendError),
        (SerializationError, CacheError),
        (CantDeserializeError, SerializationError),
        (KeyRejectedError, CacheError),
    ],
)
def test_cache_error_types_preserve_their_category(
    error_type: type[Exception], parent_type: type[Exception]
) -> None:
    assert issubclass(error_type, parent_type)
