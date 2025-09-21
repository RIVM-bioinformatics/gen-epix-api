"""Factory for creating secret providers."""

import os
from typing import Any, Type

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider.azure_key_vault import (
    AzureKeyVaultSecretProvider,
)
from gen_epix.commondb.config.secret_provider.base import (
    BaseSecretProvider,
    SecretLoadError,
)
from gen_epix.commondb.config.secret_provider.environment import (
    EnvironmentSecretProvider,
)
from gen_epix.commondb.config.secret_provider.file import FileSecretProvider


class SecretProviderFactory:
    """Factory for creating secret providers based on strategy."""

    STRATEGY_ENV_VAR = "SECRETS_STRATEGY"

    STRATEGIES: dict[str, Type[BaseSecretProvider]] = {
        "ENVIRONMENT": EnvironmentSecretProvider,
        "FILE": FileSecretProvider,
        "AZURE_KEY_VAULT": AzureKeyVaultSecretProvider,
    }

    @classmethod
    def create_provider(
        cls,
        prefix: str,
        strategy: str | None = None,
        lowercase_keys: bool = True,
        strategy_env_var: str | None = None,
        **kwargs: Any,
    ) -> BaseSecretProvider:
        """
        Create a secret provider based on strategy.

        Args:
            prefix: Prefix for app-specific environment variables
            strategy: Secret strategy ('environment', 'file', 'azure_key_vault').
                If None, uses {APP_PREFIX}_SECRETS_STRATEGY env var. Only one strategy
                may be specified in the env var for this method.

        Returns:
            Secret provider instance

        Raises:
            SecretLoadError: If strategy is invalid or not specified
        """
        # Get strategy from environment variable if not provided
        strategy_env_var = strategy_env_var or cls.STRATEGY_ENV_VAR
        if strategy is None:
            env_var = f"{prefix.upper()}{strategy_env_var}"
            strategy = os.environ.get(env_var)
            if not strategy:
                raise SecretLoadError(
                    f"Secret strategy not specified, or multiple strategies found. Set environment variable {env_var} to one of: "
                    f"{', '.join(cls.STRATEGIES.keys())}"
                )
        # Get provider class
        strategy = strategy.upper()
        if strategy not in cls.STRATEGIES:
            raise SecretLoadError(
                f"Invalid secret strategy '{strategy}'. "
                f"Valid strategies are: {', '.join(cls.STRATEGIES.keys())}"
            )
        provider_class = cls.STRATEGIES[strategy]

        return provider_class(prefix=prefix, lowercase_keys=lowercase_keys, **kwargs)

    @classmethod
    def load_secrets(
        cls,
        prefix: str,
        strategy: list[str] | str | None = None,
        lowercase_secret_name: bool = True,
        strategy_env_var: str | None = None,
        **kwargs: Any,
    ) -> DictProxy:
        """Convenience method to create provider(s) and load secrets consecutively.

        Args:
            prefix: Prefix for app-specific environment variables
            strategies: Secret strategies. If None, uses {prefix}{STRATEGY_ENV_VAR} env var.

        Returns:
            Dictionary with loaded secrets
        """
        if isinstance(strategy, list):
            if len(set(strategy)) != len(strategy):
                raise SecretLoadError("Duplicate strategies specified")
            secrets = DictProxy()
            for curr_strategy in strategy:
                provider = cls.create_provider(
                    prefix=prefix,
                    strategy=curr_strategy,
                    lowercase_keys=lowercase_secret_name,
                    strategy_env_var=strategy_env_var,
                    **kwargs,
                )
                secrets.update(provider.load_secrets())
            return secrets
        provider = cls.create_provider(
            prefix=prefix,
            strategy=strategy,
            lowercase_keys=lowercase_secret_name,
            strategy_env_var=strategy_env_var,
            **kwargs,
        )
        return provider.load_secrets()
