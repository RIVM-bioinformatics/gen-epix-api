"""Settings manager for handling application settings."""

import json
import os
from pathlib import Path
from typing import Any, Callable

from dynaconf import Dynaconf


class SettingsManager:
    """Manages application settings with environment variable overrides."""

    DEFAULT_SETTINGS_FILES_ENVVAR = "SETTINGS_FILES"
    DEFAULT_ENVVAR_SEPARATOR = "__"

    def __init__(self, prefix: str, lowercase_keys: bool = True):
        """
        Initialize settings manager.
        """
        self.prefix = prefix
        self._settings_cache: Dynaconf | None = None
        self.lowercase_keys = lowercase_keys

    def load_settings(
        self,
        settings_files: list[str] | str | None = None,
        settings_files_envvar: str | None = None,
        envvar_separator: str | None = None,
        post_hooks: Callable | list[Callable] | None = None,
    ) -> Dynaconf:
        """
        Load settings from one or more settings file(s) specified either as a
        list or if not, in an environment variable.
        """
        settings_files_envvar = (
            settings_files_envvar or self.DEFAULT_SETTINGS_FILES_ENVVAR
        )
        envvar_separator = envvar_separator or self.DEFAULT_ENVVAR_SEPARATOR
        # Determine settings files to use
        if settings_files is None:
            # Try to get from environment variable
            settings_files = os.environ.get(f"{self.prefix}{settings_files_envvar}")
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
                f"environment variable {self.prefix}{settings_files_envvar}"
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
            envvar_separator=envvar_separator,  # Support nested keys like API__HOST
            lowercase_read=self.lowercase_keys,  # Ensure keys are lowercase for Pydantic
            ignore_unknown_envvars=True,
            merge_enabled=True,
            post_hooks=post_hooks,
        )
        self._settings_cache = settings

        return self._settings_cache

    @property
    def settings(self) -> Dynaconf:
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
