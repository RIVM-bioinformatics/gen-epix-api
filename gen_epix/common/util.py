import json
import tomllib
import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Hashable, Iterable, Type

import ulid
from pydantic import BaseModel, Field

from gen_epix.fastapp import Command, Domain, Model, exc


def generate_ulid() -> uuid.UUID:
    return ulid.api.new().uuid


def get_project_root() -> Path:
    """
    Get the root path of the project by looking for pyproject.toml.

    Searches upward from the current file's directory until it finds
    a directory containing pyproject.toml, which indicates the project root.

    Returns:
        Path: The absolute path to the project root directory.

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found in any parent directory.
    """
    current_dir = Path(__file__).parent

    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            return current_dir.resolve()
        current_dir = current_dir.parent

    raise FileNotFoundError("Could not find pyproject.toml in any parent directory")


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
        path = Path(file)
        if not path.is_file():
            continue
        with open(path, "r", encoding="utf-8") as handle:
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
    """Retrieve the project version from the pyproject.toml file.
    Must be run from the project root directory.

    Returns:
        str: The version of the project as specified in pyproject.toml.
    """
    pyproject_path = "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    return pyproject_data["project"]["version"]


def register_domain_entities(
    domain: Domain,
    sorted_service_types: Iterable[Hashable],
    sorted_models_by_service_type: dict[Hashable, list[Type[Model]]],
    commands_by_service_type: dict[Hashable, set[Type[Command]]],
    common_model_impl: dict[Type[Model], Type[Model]] | None = None,
    common_command_impl: dict[Type[Command], Type[Command]] | None = None,
    set_schema_to_service_type: bool = False,
) -> None:
    """
    Register service types, models and commands with a domain. In case some
    models or commands are subclassed from another domain and the provides
    models and commands contain their parent classes, they can be substituted
    in the input and subsequently be registered as the actual classes, by
    providing a mapping.

    If `set_schema_to_service_type` is enabled, the schema name of the model
    will be set to the lower case service name for persistable entities, unless
    the schema name is already set.
    """
    if not common_model_impl:
        common_model_impl = {}
    for service_type in sorted_service_types:
        # Register the service type
        domain.register_service_type(service_type)
        schema_name = (
            str(service_type.value).lower()
            if isinstance(service_type, Enum)
            else str(service_type)
        )
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
            if (
                set_schema_to_service_type
                and model_class.ENTITY.persistable
                and model_class.ENTITY.schema_name is None
            ):
                model_class.ENTITY.schema_name = schema_name
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


def copy_model_field(
    from_model: Type[BaseModel], field_name: str, **kwargs: Any
) -> Any:
    """
    Copy a field from a model
    """
    field_info_attributes = {
        "alias": "alias",
        "alias_priority": "alias_priority",
        "default": "default",
        "default_factory": "default_factory",
        "deprecated": "deprecated",
        "description": "description",
        "discriminator": "discriminator",
        "examples": "examples",
        "exclude": "exclude",
        "frozen": "frozen",
        "init": "init",
        "init_var": "init_var",
        "json_schema_extra": "json_schema_extra",
        "kw_only": "kw_only",
        "serialization_alias": "serialization_alias",
        "title": "title",
    }
    metadata_attributes = {
        "allow_inf_nan": "allow_inf_nan",
        "coerce_numbers_to_str": "coerce_numbers_to_str",
        "decimal_places": "decimal_places",
        "ge": "ge",
        "gt": "gt",
        "le": "le",
        "lt": "lt",
        "max_digits": "max_digits",
        "max_length": "max_length",
        "min_length": "min_length",
        "multiple_of": "multiple_of",
        "pattern": "pattern",
    }
    # Currently unmapped attributes
    other_attributes = {
        "fail_fast": "fail_fast",
        "field_title_generator": "field_title_generator",
        "repr": "repr",
        "union_mode": "union_mode",
        "validate_default": "validate_default",
        "validation_alias": "validation_alias",
        "strict": "strict",
    }
    # Add field_info attributes
    field_info = from_model.model_fields[field_name]
    field_kwargs = {
        y: getattr(field_info, x)
        for x, y in field_info_attributes.items()
        if getattr(field_info, x) is not None
    }
    # Special case: always add default
    field_kwargs["default"] = field_info.default
    # Add field_info.metadata attributes
    for metadata in field_info.metadata:
        for x, y in metadata_attributes.items():
            if hasattr(metadata, x):
                field_kwargs[y] = getattr(metadata, x)
    # Override any attributes provided in kwargs
    field_kwargs.update(kwargs)
    # Create field
    return Field(**field_kwargs)
