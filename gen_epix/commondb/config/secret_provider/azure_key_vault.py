"""Azure Key Vault secret provider."""

import os
from typing import Any

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider.base import (
    BaseSecretProvider,
    SecretLoadError,
)
from gen_epix.commondb.config.settings.manager import SettingsManager


class AzureKeyVaultSecretProvider(BaseSecretProvider):
    """Secret provider that reads secrets from Azure Key Vault."""

    URL_ENV_VAR = "AZURE_KEYVAULT_URL"
    CLIENT_ID_ENV_VAR = "AZURE_CLIENT_ID"
    CLIENT_SECRET_ENV_VAR = "AZURE_CLIENT_SECRET"
    TENANT_ID_ENV_VAR = "AZURE_TENANT_ID"

    def __init__(self, prefix: str, lowercase_keys: bool = True, **kwargs: Any):
        """
        Initialize Azure Key Vault secret provider.

        Args:
            prefix: Prefix for required environment variables
        """
        super().__init__(prefix, lowercase_keys=lowercase_keys)
        self._client: Any = None

    def _get_client(self) -> Any:
        """Get Azure Key Vault client."""
        if self._client is not None:
            return self._client

        try:
            from azure.identity import ClientSecretCredential, DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
        except ImportError:
            raise SecretLoadError(
                "Azure Key Vault dependencies not installed. "
                "Install with: pip install azure-keyvault-secrets azure-identity"
            )

        # Get configuration from environment variables
        vault_url = os.environ.get(self.URL_ENV_VAR)
        if not vault_url:
            raise SecretLoadError(f"Environment variable {self.URL_ENV_VAR} not set")

        # Try client secret authentication first, fall back to default credential
        client_id = os.environ.get(self.CLIENT_ID_ENV_VAR)
        client_secret = os.environ.get(self.CLIENT_SECRET_ENV_VAR)
        tenant_id = os.environ.get(self.TENANT_ID_ENV_VAR)

        try:
            if client_id and client_secret and tenant_id:
                # Use client secret credential
                credential: ClientSecretCredential | DefaultAzureCredential = (
                    ClientSecretCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret,
                    )
                )
            else:
                # Use default credential (managed identity, CLI, etc.)
                credential = DefaultAzureCredential()

            self._client = SecretClient(vault_url=vault_url, credential=credential)
            return self._client

        except Exception as e:
            raise SecretLoadError(f"Failed to create Azure Key Vault client: {e}")

    def load_secrets(self) -> DictProxy:
        """Load secrets from Azure Key Vault.

        Secret names in Key Vault must start with the app prefix (case-insensitive)
        and use dash separation for paths. Two dashes are converted to a single
        underscore.
        JSON values are parsed, otherwise treated as strings.
        """
        client = self._get_client()

        secrets = DictProxy()

        try:
            # List all secrets in the vault
            secret_properties = client.list_properties_of_secrets()

            for secret_property in secret_properties:
                secret_name = secret_property.name

                # Skip secrets that don't start with prefix or are None
                if not secret_name or not secret_name.lower().startswith(
                    self.prefix.lower()
                ):
                    continue

                try:
                    # Get the secret value as lower case
                    secret = client.get_secret(secret_name)
                    value = secret.value

                    # Convert secret name to path
                    key_path = (
                        secret_name[len(self.prefix) :]
                        .replace("--", "_")
                        .replace("-", ".")
                    )
                    if self.lowercase_keys:
                        key_path = key_path.lower()

                    # Try to parse value as JSON, fall back to string
                    value = SettingsManager.parse_json(value)

                    # Create nested structure
                    secrets[key_path] = value

                except Exception as e:
                    # Log error but continue with other secrets
                    print(f"Warning: Failed to retrieve secret {secret_name}: {e}")
                    continue

        except Exception as e:
            raise SecretLoadError(f"Failed to load secrets from Azure Key Vault: {e}")

        if not secrets:
            raise SecretLoadError(
                "No secrets found in Azure Key Vault with 'secret-' prefix"
            )

        self._secrets_cache = secrets
        return secrets
