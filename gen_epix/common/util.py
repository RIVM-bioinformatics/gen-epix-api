import json
import tomllib
import uuid
from pathlib import Path
from typing import Any, Hashable, Iterable, Type

import ulid
from pkg_resources import DistributionNotFound, get_distribution

from gen_epix.fastapp import Command, Domain, Model, exc


def generate_ulid() -> uuid.UUID:
    return ulid.api.new().uuid


def map_paired_elements(
    data: Iterable[tuple[Hashable, Any]], as_set: bool = False, frozen: bool = False
) -> (
    dict[Hashable, list[Any]]
    | dict[Hashable, set[Any]]
    | dict[Hashable, frozenset[Any]]
):
    """
    Convert an iterable of paired elements to a dictionary of lists or sets, where
    the keys are the unique first elements and the values the list or set of second
    elements matching that key in the input. If frozen=True, the sets are converted
    to frozensets.
    """
    retval: (
        dict[Hashable, list[Any]]
        | dict[Hashable, set[Any]]
        | dict[Hashable, frozenset[Any]]
    ) = {}
    if as_set:
        for k, v in data:
            if k not in retval:
                retval[k] = set()  # type: ignore[assignment]
            retval[k].add(v)  # type: ignore[union-attr]
        if frozen:
            for k in retval:
                retval[k] = frozenset(retval[k])  # type: ignore[assignment]
    else:
        for k, v in data:
            if k not in retval:
                retval[k] = []  # type: ignore[assignment]
            retval[k].append(v)  # type: ignore[union-attr]
    return retval


def update_cfg_from_file(
    cfg: dict,
    file_or_dir: str,
    cfg_key_map: None | dict[str, str] = None,
    file_key_delimiter: str = "-",
) -> None:
    """
    Import values from files as a nested dict where the nested keys are the file
    name split by "-". The value of the innermost key is the content of the file,
    which can in turn again be a dict.
    """
    cfg_key_map = cfg_key_map or {}

    def _add_value_recursion(cfg: dict, new_cfg: dict, parent_path: str) -> None:
        # Recursively add/replace values to/in cfg
        for key, value in new_cfg.items():
            path = f"{parent_path}.{key}" if len(parent_path) else key
            key = cfg_key_map.get(key, key)
            if isinstance(value, dict):
                if key not in cfg:
                    cfg[key] = {}
                _add_value_recursion(cfg[key], value, path)
            else:
                cfg[key] = value

    # Get list of files
    if Path(file_or_dir).is_file():
        files = [file_or_dir]
    elif Path(file_or_dir).is_dir():
        files = [str(Path(file_or_dir) / x) for x in Path(file_or_dir).iterdir()]
    else:
        raise ValueError(f"Invalid file_or_dir: {file_or_dir}")

    # Read files into new_cfg
    new_cfg: dict[str, Any] = {}
    for file in files:
        name = Path(file).name
        keys = [cfg_key_map.get(x, x) for x in name.split(file_key_delimiter)]
        curr_cfg = new_cfg
        for key in keys[0:-1]:
            if key not in curr_cfg:
                curr_cfg[key] = {}
            curr_cfg = curr_cfg[key]
        with open(Path(file), "r") as handle:
            try:
                value = json.load(handle)
            except json.JSONDecodeError as e:
                print(f"Error reading {file}: {e}\nSkipping file")
                continue
        curr_cfg[keys[-1]] = value

    # Recursively add/replace values in cfg
    _add_value_recursion(cfg, new_cfg, "")


# Get version with fallback for development
def get_package_version() -> str:
    version: str
    try:
        version = get_distribution("Gen-EpiX").version
    except DistributionNotFound:
        # Fallback version for development when package is not installed
        dir = Path(__file__).parent
        file = dir / "pyproject.toml"
        while dir.parent != dir:
            if (file := dir / "pyproject.toml").exists():
                break
        if file.exists():
            raise FileNotFoundError(
                f"Could not find pyproject.toml in {dir} or its parent directories."
            )
        with open(file, "rb") as handle:
            version: str = tomllib.load(handle)["project"]["version"]
    return version


def register_domain_entities(
    domain: Domain,
    sorted_service_types: Iterable[Hashable],
    sorted_models_by_service_type: dict[Hashable, list[Type[Model]]],
    commands_by_service_type: dict[Hashable, set[Type[Command]]],
    common_model_impl: dict[Type[Model], Type[Model]] | None = None,
    common_command_impl: dict[Type[Command], Type[Command]] | None = None,
) -> None:
    """
    Register service types, models and commands with a domain. In case some
    models or commands are subclassed from another domain and the provides
    models and commands contain their parent classes, they can be substituted
    in the input and subsequently be registered as the actual classes, by
    providing a mapping.
    """
    if not common_model_impl:
        common_model_impl = {}
    for service_type in sorted_service_types:
        # Register the service type
        domain.register_service_type(service_type)
        # Register the models
        for i, model_class in enumerate(
            sorted_models_by_service_type.get(service_type, [])
        ):
            if model_class in common_model_impl:
                # Substitute the model class with its common implementation,
                # also in the input
                model_class = common_model_impl[model_class]
                sorted_models_by_service_type[service_type][i] = model_class
            if model_class.ENTITY is None:
                raise exc.InitializationServiceError(
                    f"Entity for model class {model_class} is not initialized."
                )
            domain.register_entity(
                model_class.ENTITY, model_class=model_class, service_type=service_type
            )
        # Register the commands
        for command_class in commands_by_service_type.get(service_type, []):
            if common_command_impl and command_class in common_command_impl:
                # Substitute the command class with its common implementation,
                # also in the input
                commands_by_service_type[service_type].remove(command_class)
                command_class = common_command_impl[command_class]
                commands_by_service_type[service_type].add(command_class)
            domain.register_command(command_class, service_type=service_type)
