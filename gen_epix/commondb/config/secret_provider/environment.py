"""Environment variable based secret provider."""

import os

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider.base import (
    BaseSecretProvider,
    SecretLoadError,
)
from gen_epix.commondb.config.settings.manager import SettingsManager


class EnvironmentSecretProvider(BaseSecretProvider):
    """Secret provider that reads secrets from environment variables."""

    def load_secrets(self) -> DictProxy:
        """
        Load secrets from environment variables.
        Environment variables must follow the pattern:
        {PREFIX}{PATH} where PATH uses double underscores for nesting.
        JSON values are parsed, otherwise treated as strings.
        """
        secrets = DictProxy()

        for env_var, value in os.environ.items():
            if env_var.startswith(self.prefix):
                # Remove prefix and convert to path
                secret_path = env_var[len(self.prefix) :]
                # Convert double underscores to dots for nesting
                key_path = secret_path.replace("__", ".")
                if self.lowercase_keys:
                    key_path = key_path.lower()

                # Try to parse as JSON first, fall back to string
                parsed_value = SettingsManager.parse_json(value)

                secrets[key_path] = parsed_value

        if not secrets._data:
            raise SecretLoadError(
                f"No secrets found with prefix {self.prefix}. "
                f"Environment variables should start with {self.prefix}"
            )

        self._secrets_cache = secrets
        return secrets
