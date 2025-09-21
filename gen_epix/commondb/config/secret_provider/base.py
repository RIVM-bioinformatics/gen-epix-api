"""Abstract base class for secret providers."""

from abc import ABC, abstractmethod
from typing import Any

from gen_epix.commondb.config.dict_proxy import DictProxy


class BaseSecretProvider(ABC):
    """Abstract base class for secret management strategies."""

    def __init__(self, prefix: str, lowercase_keys: bool = True, **kwargs: Any):
        """Initialize secret provider.

        Args:
            app_prefix: Prefix for environment variables or secrets
        """
        self.prefix = prefix
        self.lowercase_keys = lowercase_keys
        self._secrets_cache: DictProxy | None = None

    @abstractmethod
    def load_secrets(self) -> DictProxy:
        """Load all secrets."""
        pass

    def get_secret(self, key_path: str) -> Any | None:
        """Get a specific secret by path.

        Args:
            key_path: dot-separated path to secret (e.g., 'db.repository_type')

        Returns:
            Secret value or None if not found
        """
        if self._secrets_cache is None:
            try:
                self.load_secrets()
            except SecretLoadError:
                return None
        assert self._secrets_cache is not None

        try:
            return self._secrets_cache[key_path]
        except (KeyError, TypeError):
            return None
        pass


class SecretLoadError(Exception):
    """Exception raised when secrets cannot be loaded."""

    pass
