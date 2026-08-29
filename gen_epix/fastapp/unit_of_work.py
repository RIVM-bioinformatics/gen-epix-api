"""Unit-of-work interface for transactional repository operations."""

import abc
from types import TracebackType
from typing import Self


class BaseUnitOfWork(abc.ABC):
    """Provide the base unit of work framework abstraction."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self._is_managing_context: bool = False

    @property
    def is_managing_context(self) -> bool:
        """Perform the is managing context operation."""
        return self._is_managing_context

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction. This method should be implemented by subclasses
        to define the specific behavior for committing a transaction.

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def rollback(self) -> None:
        """
        Rollback the current transaction. This method should be implemented by subclasses
        to define the specific behavior for rolling back a transaction.

        """
        raise NotImplementedError()

    def flush(self) -> None:
        """Perform the flush operation."""
        pass

    def __enter__(self) -> Self:
        """Enter the managed context."""
        self._is_managing_context = True
        return self

    def __exit__(
        self,
        exception_class: type[Exception] | None,
        exception_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the managed context."""
        self._is_managing_context = False
        if exception_class is None:
            self.commit()
        else:
            self.rollback()
            raise exception_value.with_traceback(traceback)
