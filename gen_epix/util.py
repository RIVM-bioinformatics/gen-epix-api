import hashlib
import tomllib
import uuid
from collections import defaultdict
from collections.abc import Hashable, Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

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
    )
    if as_set:
        retval = defaultdict(set)
        for k, v in data:
            retval[k].add(v)
        if frozen:
            return {x: frozenset(y) for x, y in retval.items()}
        return dict(retval)
    retval = defaultdict(list)
    for k, v in data:
        retval[k].append(v)
    return dict(retval)


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


def add_parent_class_docs(
    cls: type | set[type],
    exclude: Iterable[type] | None = (BaseModel,),
) -> str | None:
    """
    Append the documentation of any non-excluded parent classes to the given
    class or classes' docstring. The object parent class is always excluded. If
    set_docs is True, the combined docstring is set as the class' docstring.
    """
    if exclude is None:
        exclude = set()
    elif not isinstance(exclude, set):
        exclude = set(x for x in exclude)
    exclude.add(object)
    # Handle list of classes: collect all bases and create directed acyclic graph of
    # inheritance. Then update docstrings in DAG order.
    if isinstance(cls, set):
        # Collect all parent classes
        class_bases_map: dict[type, set[type]] = {}
        for curr_class in cls:
            classes_to_process = [curr_class]
            while classes_to_process:
                curr_class = classes_to_process.pop()
                if curr_class in class_bases_map:
                    continue
                parent_classes = tuple(
                    x for x in curr_class.__bases__ if x not in exclude
                )
                class_bases_map[curr_class] = set(parent_classes)
                classes_to_process.extend(parent_classes)
        # Create DAG order
        dag_order: list[type] = []
        processed_classes: set[type] = set()
        while len(processed_classes) < len(class_bases_map):
            for curr_class, parents in class_bases_map.items():
                if curr_class in processed_classes:
                    continue
                if all(x in processed_classes for x in parents):
                    dag_order.append(curr_class)
                    processed_classes.add(curr_class)
        # Update docstrings in DAG order
        for curr_class in dag_order:
            if len(class_bases_map[curr_class]) == 0:
                continue
            add_parent_class_docs(curr_class, exclude=exclude)
        return None
    # Single class
    doc = cls.__doc__
    parent_classes = cls.__bases__
    parent_classes = tuple(x for x in parent_classes if x not in exclude)
    parent_docs = []
    for parent_class in parent_classes:
        parent_doc = parent_class.__doc__
        if parent_doc is None or parent_doc.strip() == "":
            continue
        parent_docs.append(f"{parent_class.__name__}:\n{parent_doc}")
    if parent_docs:
        if doc is None:
            doc = ""
        else:
            doc = doc.strip() + "\n\n\n\n"
        doc = doc + "PARENT CLASS DOCUMENTATION\n\n\n" + "\n\n\n".join(parent_docs)
        cls.__doc__ = doc
    return doc


def str_to_uuid(value: str) -> UUID:
    """
    Convert a string to a UUID by encoding it as UTF-8, then calculating the SHA256
    hash from that and subsequently taking the first 16 bytes of the hash to construct
    the UUID.
    """
    return UUID(hashlib.sha256(value.encode("utf-8")).digest()[:16].hex())


def int_to_uuid(value: int) -> UUID:
    """
    Convert an integer to a UUID by representing it as 8 bytes, unsigned, big endian
    byte order and constructing the UUID from that.
    """
    return UUID(
        hashlib.sha256(value.to_bytes(length=8, byteorder="big", signed=False))
        .digest()[:16]
        .hex()
    )


def chunk_list(values: list, chunk_size: int | None) -> list[list]:
    """Split *values* into sub-lists of at most *chunk_size*.

    Returns ``[values]`` when *chunk_size* is ``None`` (no
    chunking). Returns ``[]`` when *values* is empty so
    callers can skip the loop entirely.
    """
    if not values:
        return []
    if chunk_size is None:
        return [values]
    n = len(values)
    return [values[i : i + chunk_size] for i in range(0, n, chunk_size)]
