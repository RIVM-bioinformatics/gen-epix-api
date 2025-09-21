"""File system based secret provider."""

import os
from pathlib import Path
from typing import Any

from gen_epix.commondb.config.dict_proxy import DictProxy
from gen_epix.commondb.config.secret_provider.base import (
    BaseSecretProvider,
    SecretLoadError,
)
from gen_epix.commondb.config.settings.manager import SettingsManager


class FileSecretProvider(BaseSecretProvider):
    """Secret provider that reads secrets from file system."""

    SECRETS_PATH_ENV_VAR = "SECRETS_PATH"
    FILE_SUFFIXES = {".json", ".txt"}

    def __init__(
        self,
        prefix: str = "",
        lowercase_keys: bool = True,
        secrets_path: str | None = None,
        file_suffixes: set[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize file system secret provider.
        The secrets_path can be provided directly or via an environment
        variable, and may not contain dots since these are used to denote nesting.
        The environment variable name is constructed as {PREFIX}{SECRETS_PATH_SUFFIX}.
        """
        super().__init__(prefix, lowercase_keys=lowercase_keys)
        self.secrets_path = secrets_path
        self._file_suffixes = {
            x.lower()
            for x in (
                file_suffixes if file_suffixes is not None else self.FILE_SUFFIXES
            )
        }

    def _get_secrets_path(self) -> Path:
        """Get the secrets directory path."""

        if self.secrets_path:
            path = Path(self.secrets_path)
        else:
            env_var = f"{self.prefix}{self.SECRETS_PATH_ENV_VAR}"
            path_str = os.environ.get(env_var)
            if not path_str:
                raise SecretLoadError(f"Environment variable {env_var} not set")
            path = Path(path_str)

        if not path.exists():
            raise SecretLoadError(f"Secrets path does not exist: {path}")

        if not path.is_dir():
            raise SecretLoadError(f"Secrets path is not a directory: {path}")

        return path

    def load_secrets(self) -> DictProxy:
        """
        Load secrets from file.
        Files must be named according to their secret path, with a .json extension for JSON files.
        The file dir and name together express the path, whereby both path separators
        and dashes in the file name are used for nesting, e.g.:
        service/repository-type.json  # Key: service.repository.type
        A double dash in the file name is converted to a single underscore, to
        accommodate situations where underscores are not allowed in file names, such as Azure key
        vault secrets exposed as files.
        """
        secrets_path = self._get_secrets_path()
        secrets: dict[str, Any] = {}

        def _read_directory(
            current_path: Path, current_dict: dict[str, Any], path_parts: list[str]
        ) -> None:
            """Recursively read directory structure."""
            for item in current_path.iterdir():
                # Convert path to nested keys
                item_relative_path = item.relative_to(secrets_path)
                dir_key_path = (
                    str(item_relative_path.parent)
                    if item_relative_path.parent != Path(".")
                    else ""
                )
                if dir_key_path:
                    dir_key_path = dir_key_path.replace(os.sep, ".") + "."
                if item.is_file():
                    # Read file content as secret value
                    try:
                        with open(item, "r", encoding="utf-8") as handle:
                            content = handle.read().strip()
                    except (IOError, OSError) as e:
                        raise SecretLoadError(f"Failed to read secret file {item}: {e}")

                    # Convert file name to nested keys, removing known suffix and using dashes as separator
                    suffix = ""
                    if item.suffix.lower() in self._file_suffixes:
                        suffix = item.suffix
                    basename = item.name[0 : -len(suffix)] if suffix else item.name

                    # Build full key path
                    key_path = dir_key_path + basename.replace("--", "_").replace(
                        "-", "."
                    )
                    if self.lowercase_keys:
                        key_path = key_path.lower()

                    # Parse as JSON in case of complex types
                    try:
                        content = SettingsManager.parse_json(content)
                    except Exception:
                        # If JSON parsing fails, keep as string
                        pass

                    current_dict[key_path] = content
                elif item.is_dir():
                    # Create nested dictionary for subdirectory
                    current_dict[item.name] = DictProxy()
                    _read_directory(
                        item, current_dict[item.name], path_parts + [item.name]
                    )

        try:
            _read_directory(secrets_path, secrets, [])
        except Exception as e:
            if isinstance(e, SecretLoadError):
                raise
            raise SecretLoadError(f"Failed to load secrets from {secrets_path}: {e}")

        if not secrets:
            raise SecretLoadError(f"No secrets found in {secrets_path}")

        secrets_proxy = DictProxy(secrets)
        self._secrets_cache = secrets_proxy
        return secrets_proxy
