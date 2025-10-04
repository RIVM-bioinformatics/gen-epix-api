"""Settings manager for handling application settings."""

import json
import os
import re
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf

from gen_epix.commondb.config.dict_proxy import DictProxy


class SettingsManager:
    """Manages application settings with environment variable overrides."""

    SETTINGS_FILES_ENV_VAR = "SETTINGS_FILES"
    DYNACONF_EXCLUDE_PATTERN = re.compile("DYNACONF")

    def __init__(self, prefix: str, lowercase_keys: bool = True):
        """
        Initialize settings manager.
        """
        self.prefix = prefix
        self._settings_cache: DictProxy | None = None
        self.lowercase_keys = lowercase_keys

    def load_settings(
        self,
        settings_files: list[str] | str | None = None,
        settings_files_env_var: str | None = None,
    ) -> DictProxy:
        """
        Load settings from one or more settings file(s) specified either as a
        list or if not, in an environment variable.
        """
        settings_files_env_var = settings_files_env_var or self.SETTINGS_FILES_ENV_VAR
        # Determine settings files to use
        if settings_files is None:
            # Try to get from environment variable
            settings_files = os.environ.get(f"{self.prefix}{settings_files_env_var}")
            if settings_files:
                settings_files = SettingsManager.parse_json(settings_files)
        elif isinstance(settings_files, list):
            pass
        else:
            settings_files = SettingsManager.parse_json(settings_files)
        if isinstance(settings_files, str):
            settings_files = [settings_files]
        if not settings_files:
            raise ValueError(
                "No settings files provided. Specify via argument or "
                f"environment variable {self.prefix}{settings_files_env_var}"
            )
        for settings_file_path in settings_files:
            if not Path(settings_file_path).exists():
                raise FileNotFoundError(
                    f"Custom settings file not found: {settings_file_path}"
                )

        # Load settings using dynaconf for environment variable support
        settings = Dynaconf(
            envvar_prefix=self.prefix,
            settings_files=settings_files,
            load_dotenv=True,
            envvar_separator="__",  # Support nested keys like API__HOST
            lowercase_read=self.lowercase_keys,  # Ensure keys are lowercase for Pydantic
            ignore_unknown_envvars=True,
        )
        # Dynaconf conversion to dict does not preserve key casing, so we re-load with lowercase keys if needed
        self._settings_cache = DictProxy()

        # Convert dynaconf to dict for pydantic validation
        self._settings_cache = DictProxy(data=dict(settings))

        # Validate with pydantic schema
        # self._settings = SettingsSchema(**self._settings_cache)

        return self._settings_cache

    @property
    def settings(self) -> DictProxy:
        """Get loaded settings."""
        if self._settings_cache is None:
            raise RuntimeError("Settings not loaded. Call load_settings() first.")
        return self._settings_cache

    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get setting value by dot-notation path.

        Args:
            key_path: Dot-separated path to setting (e.g., 'api.host')
            default: Default value if not found

        Returns:
            Setting value or default
        """
        if self._settings_cache is None:
            raise RuntimeError("Settings not loaded. Call load_settings() first.")
        try:
            return self._settings_cache[key_path]
        except (KeyError, TypeError):
            return default

    @staticmethod
    def parse_json(content: str, allow_str: bool = False) -> Any:
        """
        Parse content as JSON if possible, otherwise return as string.
        """
        if (
            (content.startswith("{") and content.endswith("}"))
            or (content.startswith("[") and content.endswith("]"))
            or (content.startswith('"') and content.endswith('"'))
        ):
            return json.loads(content)
        return content
