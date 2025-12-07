import tomllib
import uuid
from collections.abc import Hashable, Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any

import ulid
from pydantic import BaseModel, Field


def generate_ulid() -> uuid.UUID:
    return ulid.api.new().uuid


def get_package_root() -> Path:
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


@lru_cache(maxsize=1)
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


def copy_model_field(
    from_model: type[BaseModel], field_name: str, **kwargs: Any
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
