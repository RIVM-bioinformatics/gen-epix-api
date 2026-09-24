"""Provide shared helpers for identifiers, models, collections, and profiling.

Identifier helpers generate sortable UUIDs or deterministically map strings and
integers to UUIDs. Model helpers copy Pydantic field configuration and combine
inherited class documentation. Collection helpers group paired values and split
lists into batches. The profiling decorator records synchronous or asynchronous
call executions without changing their results or exceptions.
"""

import datetime
import hashlib
import inspect
import tomllib
import uuid
from collections import defaultdict
from collections.abc import Hashable, Iterable
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import ulid
from pydantic import BaseModel, Field
from pyinstrument import Profiler


def generate_ulid() -> uuid.UUID:
    """Generate a new UUID backed by a ULID.

    Returns:
        A UUID whose underlying ULID preserves creation-time ordering.
    """
    return ulid.api.new().uuid


def get_package_root() -> Path:
    """Return the repository root located from this module's source path.

    Searches parent directories for ``pyproject.toml`` rather than depending on
    the caller's current working directory.

    Returns:
        Absolute path to the directory containing ``pyproject.toml``.

    Raises:
        FileNotFoundError: If no parent directory contains ``pyproject.toml``.
    """
    current_dir = Path(__file__).parent

    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            return current_dir.resolve()
        current_dir = current_dir.parent

    raise FileNotFoundError("Could not find pyproject.toml in any parent directory")


@lru_cache(maxsize=1)
def get_package_version() -> str:
    """Retrieve the project version from the project metadata.

    The function reads ``pyproject.toml`` relative to the current working
    directory and caches the first successful result for the process.

    Returns:
        The version declared under ``project.version``.

    Raises:
        FileNotFoundError: If the current directory lacks the project metadata
            file.
        KeyError: If the metadata does not define the expected project version.
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
    """Group paired values by key while preserving input order for lists.

    With ``as_set=False``, repeated values are retained in encounter order.
    With ``as_set=True``, repeated values are removed. Setting ``frozen=True``
    changes set values to frozensets and has no effect when ``as_set`` is false.

    Args:
        data: Iterable of key-value pairs to group.
        as_set: Whether each grouped value should be a set instead of a list.
        frozen: Whether set values should be immutable frozensets.

    Returns:
        A dictionary mapping each encountered key to its grouped values.
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
    """Create a Pydantic field with copied configuration from another model.

    Field metadata and supported ``Field`` attributes are copied before any
    keyword arguments supplied by the caller are applied as overrides.

    Args:
        from_model: Model whose field definition supplies the defaults.
        field_name: Name of the field to copy from ``from_model``.
        **kwargs: Field attributes that override copied values.

    Returns:
        A new Pydantic field definition.

    Raises:
        KeyError: If ``field_name`` is not defined on ``from_model``.
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
    """Append inherited documentation to one class or a class hierarchy.

    Excluded classes and ``object`` are omitted. For a set of classes, parents
    are processed before children so inherited documentation is available when
    each child is updated. The single-class form mutates ``cls.__doc__`` only
    when at least one eligible parent has documentation. A supplied set of
    excluded classes is also mutated to include ``object``.

    Args:
        cls: Class to update, or classes whose inheritance graph should be
            processed in dependency order.
        exclude: Classes whose documentation should not be inherited.

    Returns:
        The updated docstring for a single class, or ``None`` for a class set.
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
    """Derive a deterministic UUID from a UTF-8 string.

    The SHA-256 digest is truncated to the 16 bytes required by UUID. Different
    strings normally produce different UUIDs, while repeated inputs produce the
    same value.

    Args:
        value: String from which to derive the UUID.

    Returns:
        A deterministic UUID derived from ``value``.
    """
    return UUID(hashlib.sha256(value.encode("utf-8")).digest()[:16].hex())


def int_to_uuid(value: int) -> UUID:
    """Derive a deterministic UUID from an unsigned 64-bit integer.

    The integer is encoded as eight big-endian bytes, hashed with SHA-256, and
    truncated to the 16 bytes required by UUID.

    Args:
        value: Non-negative integer that fits in eight bytes.

    Returns:
        A deterministic UUID derived from ``value``.

    Raises:
        OverflowError: If ``value`` is negative or does not fit in eight bytes.
    """
    return UUID(
        hashlib.sha256(value.to_bytes(length=8, byteorder="big", signed=False))
        .digest()[:16]
        .hex()
    )


def chunk_list(values: list, chunk_size: int | None) -> list[list]:
    """Split values into sub-lists of at most ``chunk_size``.

    A ``None`` chunk size returns the original list inside a one-item list.
    Empty input returns an empty list so callers can skip iteration entirely.

    Args:
        values: List to divide into chunks.
        chunk_size: Maximum number of items per chunk, or ``None`` to disable
            chunking.

    Returns:
        The input values divided into consecutive chunks.
    """
    if not values:
        return []
    if chunk_size is None:
        return [values]
    n = len(values)
    return [values[i : i + chunk_size] for i in range(0, n, chunk_size)]


def profile_method(path: str | None = None) -> Callable:
    """Profile a callable and write its report to a timestamped log file.

    The returned decorator detects whether the wrapped callable is synchronous
    or asynchronous, forwards its arguments and return value unchanged, and
    writes a report even when the callable raises. When no path is provided,
    reports are written at the repository root.

    Args:
        path: Directory in which profiling logs should be created, or ``None``
            to use the project root.

    Returns:
        A decorator that profiles the wrapped callable.
    """
    file_path = Path(path) if path else get_package_root()

    def _write_profile(profiler: Profiler, method_name: str) -> None:
        """Write profiler output to a timestamped log file."""
        filename = (
            f"{method_name}-"
            f"{datetime.datetime.now(tz=datetime.timezone.utc):%Y-%m-%d_%H-%M-%S}-"
            f"{uuid.uuid4()}.log"
        )
        with open(file_path / filename, "w", encoding="utf-8") as f:
            profiler.print(file=f, color=False)

    def decorator(method: Callable) -> Callable:
        """Wrap a callable with the appropriate profiler lifecycle."""
        if inspect.iscoroutinefunction(method):

            @wraps(method)
            async def async_wrapper(*args, **kwargs):
                """Profile an asynchronous invocation of the wrapped method."""
                profiler = Profiler(async_mode="enabled")

                profiler.start()
                try:
                    return await method(*args, **kwargs)
                finally:
                    profiler.stop()
                    _write_profile(profiler, method.__name__)

            return async_wrapper

        @wraps(method)
        def sync_wrapper(*args, **kwargs):
            """Profile a synchronous invocation of the wrapped method."""
            profiler = Profiler(async_mode="disabled")

            profiler.start()
            try:
                return method(*args, **kwargs)
            finally:
                profiler.stop()
                _write_profile(profiler, method.__name__)

        return sync_wrapper

    return decorator
