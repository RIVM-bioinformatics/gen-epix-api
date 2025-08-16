import importlib.resources
import os
from pathlib import Path


class ConfigDiscovery:
    """
    Config discovery class.
    Highest priority is the config path in the environment variable.
    Second is the local config path.
    Third is the config path in the package.
    """

    @staticmethod
    def get_config_path(
        app_type: str,
        env_var_substring: str = "",
        extension: str = "",
        verbose: bool = False,
    ) -> str:
        """
        Config path picked in the following order:
        1. Environment variable
        2. Local config path
        3. Package config path
        4. Raise error if not found
        """
        path = ConfigDiscovery.get_config_path_from_env(
            app_type, env_var_substring=env_var_substring, extension=extension
        )
        if path:
            if verbose:
                print(f"Config path found in environment variable: {path}")
            return path
        path = ConfigDiscovery.get_config_path_from_local(app_type, extension=extension)
        if path:
            if verbose:
                print(f"Config path found in local file: {path}")
            return path
        path = ConfigDiscovery.get_config_path_from_package(
            app_type, extension=extension
        )
        if path:
            if verbose:
                print(f"Config path found in package: {path}")
            return path
        raise ValueError(
            f"Config path not found for app type {app_type}. Please set the environment variable {app_type.upper()}_CONFIG_PATH."
        )

    @staticmethod
    def get_config_path_from_env(
        app_type: str, env_var_substring: str, extension: str = ""
    ) -> str | None:
        """Get config path from environment variable, if not return None."""
        env_var_name = f"{app_type.upper()}_{env_var_substring}"
        if env_var_name in os.environ:
            env_config_path = Path(os.environ[env_var_name])
            if extension:
                return str(env_config_path / extension)
            return str(env_config_path)
        return None

    @staticmethod
    def get_config_path_from_local(app_type: str, extension: str = "") -> str | None:
        """Get config path from local file, if not return None."""
        local_config_path = Path(f"./config/{app_type}")
        if local_config_path.exists():
            if extension:
                return str(local_config_path / extension)
            return str(local_config_path)
        return None

    @staticmethod
    def get_config_path_from_package(app_type: str, extension: str = "") -> str | None:
        """Get config path from package, if not return None."""
        with importlib.resources.as_file(
            importlib.resources.files("gen_epix")
        ) as package_path:
            package_config_path = package_path / app_type / "config"
        if package_config_path.exists():
            if extension:
                return str(package_config_path / extension)
            return str(package_config_path)
        return None
