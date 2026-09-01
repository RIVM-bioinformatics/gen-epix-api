"""Shared OMOP model mixins and primary-key normalization helpers."""

from typing import Annotated, Any
from uuid import UUID

from pydantic import Field

from gen_epix.util import int_to_uuid, str_to_uuid


class DataLineageMixin:
    """
    Add optional provenance and source-traceback fields to an OMOP model.
    """

    # Annotation-only: an assigned Field lingers as class attr -> pydantic shadow warning
    provenance_id: Annotated[
        UUID | None, Field(default=None, description="Provenance ID")
    ]
    source_traceback: Annotated[
        str | None,
        Field(default=None, description="Source traceback", max_length=255),
    ]


def validate_str_key_args(data: Any, uuid_field_name: str, str_field_name: str) -> Any:
    """
    Validate and synchronize string-based primary key arguments.

    Mutates ``data`` in place: derives ``uuid_field_name`` from
    ``str_field_name`` when absent, or verifies consistency when both
    are supplied.

    Args:
        data: The input data dictionary containing the primary key fields.
        uuid_field_name: The name of the UUID field in the data dictionary.
        str_field_name: The name of the string field in the data dictionary.

    Raises:
        ValueError: If the input data is not a dictionary or if the primary key fields are invalid.

    Returns:
        The normalized input data after in-place primary-key synchronization.
    """
    if not isinstance(data, dict):
        raise ValueError("Input is not a dict")
    uuid_id = data.get(uuid_field_name)
    str_id = data.get(str_field_name)
    if isinstance(uuid_id, str) and str_id is None:
        # str_id provided as uuid_id -> switch
        str_id = uuid_id
        data[str_field_name] = str_id
        uuid_id = None
    elif not isinstance(str_id, str):
        raise ValueError(f"{str_field_name} not provided or not a string")
    if uuid_id is None:
        # Derive uuid_id from str_id
        data[uuid_field_name] = str_to_uuid(str_id)
    else:
        # Verify uuid_id equal to computed one
        computed_uuid_id = str_to_uuid(str_id)
        msg = f"Provided {uuid_field_name} is not identical to the one derived from {str_field_name}"
        if isinstance(uuid_id, str):
            uuid_id = UUID(uuid_id)
            data[uuid_field_name] = uuid_id
        if uuid_id != computed_uuid_id:
            raise ValueError(msg)


def validate_int_key_args(data: Any, uuid_field_name: str, int_field_name: str) -> Any:
    """
    Validate and synchronize integer-based primary key arguments.

    Mutates ``data`` in place: derives ``uuid_field_name`` from
    ``int_field_name`` when absent, or verifies consistency when both
    are supplied.

    Args:
        data: The input data dictionary containing the primary key fields.
        uuid_field_name: The name of the UUID field in the data dictionary.
        int_field_name: The name of the integer field in the data dictionary.

    Raises:
        ValueError: If the input data is not a dictionary or if the primary key fields are invalid.

    Returns:
        The normalized input data after in-place primary-key synchronization.
    """
    if not isinstance(data, dict):
        raise ValueError("Input is not a dict")
    uuid_id = data.get(uuid_field_name)
    int_id = data.get(int_field_name)
    if isinstance(uuid_id, int) and int_id is None:
        # int_id provided as uuid_id -> switch
        int_id = uuid_id
        data[int_field_name] = int_id
        uuid_id = None
    elif int_id is None and uuid_id is not None and not isinstance(uuid_id, int):
        # UUID provided directly without an int_id → normalise to UUID object and accept
        if isinstance(uuid_id, str):
            data[uuid_field_name] = UUID(uuid_id)
        return
    elif not isinstance(int_id, int):
        raise ValueError(f"{int_field_name} not provided or not an integer")
    if uuid_id is None:
        # Derive uuid_id from int_id
        data[uuid_field_name] = int_to_uuid(int_id)
    else:
        # Verify uuid_id equal to computed one
        computed_uuid_id = int_to_uuid(int_id)
        msg = f"Provided {uuid_field_name} is not identical to the one derived from {int_field_name}"
        if isinstance(uuid_id, str):
            uuid_id = UUID(uuid_id)
            data[uuid_field_name] = uuid_id
        if uuid_id != computed_uuid_id:
            raise ValueError(msg)


def validate_int_for_uuid_field(value: Any | None) -> UUID | None:
    """
    Validate that the input value is either a UUID or an integer that can be converted to a UUID.

    Args:
        value (Any or None): The input value to validate.
    Returns:
        UUID or None: The validated UUID value.
    Raises:
        ValueError: If the input value is neither a valid UUID string nor an integer.
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    if isinstance(value, int):
        return int_to_uuid(value)
    if isinstance(value, str):
        if len(value) in {32, 36}:
            return UUID(value)
        else:
            return int_to_uuid(int(value))
    raise ValueError(
        f"Value must be a UUID, integer or a string: {value} (class {type(value)})"
    )


def validate_str_for_uuid_field(value: Any | None) -> UUID | None:
    """
    Validate that the input value is either a UUID or a string that can be converted
    to a UUID. If a string of length 32 or 36 is provided, it is first checked if it
    is a UUID string representation and converted accordingly. Otherwise, it is treated
    as a string that can be converted to a UUID.

    Args:
        value (Any or None): The input value to validate.
    Returns:
        UUID or None: The validated UUID value.
    Raises:
        ValueError: If the input value is neither a valid UUID string nor a string that can be converted to a UUID.
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        if len(value) in {32, 36}:
            try:
                return UUID(value)
            except ValueError:
                return str_to_uuid(value)
        else:
            return str_to_uuid(value)
    raise ValueError(f"Value must be a UUID or a string: {value} (class {type(value)})")
