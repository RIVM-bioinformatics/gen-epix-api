"""Utilities for the fastapp key module."""

from collections.abc import Callable
from functools import partial

from pydantic import BaseModel


class Key:
    """Provide the key framework abstraction."""

    DEFAULT_KEY_GENERATOR_SEPARATOR = "|"

    def __init__(
        self,
        field_names: str | tuple[str, ...],
        key_generator: Callable[[BaseModel], str] | None = None,
    ):
        """Initialize the instance."""
        self._field_names: tuple[str, ...] = (
            (field_names,) if isinstance(field_names, str) else field_names
        )

        def _key_generator(field_names: tuple[str, ...], obj: BaseModel) -> str:
            """Perform the  key generator operation."""
            return Key.DEFAULT_KEY_GENERATOR_SEPARATOR.join(
                f"{obj.__dict__[x]}" for x in field_names
            )

        self._key_generator: Callable[[BaseModel], str] = (
            key_generator
            if key_generator
            else partial(_key_generator, self._field_names)
        )

    @property
    def field_names(self) -> tuple[str, ...]:
        """Perform the field names operation."""
        return self._field_names

    @property
    def key_generator(self) -> Callable[[BaseModel], str]:
        """
        Get the key generator callable.

        Returns:
        -------
        Callable[[BaseModel], str]
            The callable used to generate the key from a BaseModel obj.
        """
        return self._key_generator

    def __call__(self, obj: BaseModel) -> str:
        """Perform the   call   operation."""
        return self._key_generator(obj)
