"""Unit-of-work interface for transactional repository operations."""

import abc
from types import TracebackType
from typing import Self


class BaseUnitOfWork(abc.ABC):
    """Base context manager for repository transaction boundaries."""

    def __init__(self) -> None:
        """Initialize a BaseUnitOfWork instance."""
        self._is_managing_context: bool = False

    @property
    def is_managing_context(self) -> bool:
        """Return whether managing context."""
        return self._is_managing_context

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transaction managed by this unit of work.

        Subclasses implement persistence-specific commit behavior.

        Raises:
            NotImplementedError: Always, until a concrete unit of work implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def rollback(self) -> None:
        """Roll back the transaction managed by this unit of work.

        Subclasses implement persistence-specific rollback behavior.

        Raises:
            NotImplementedError: Always, until a concrete unit of work implements it.
        """
        raise NotImplementedError()

    def flush(self) -> None:
        """Flush the requested value."""
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
        """Finish the managed transaction context.

        Commits when the context exits normally. Rolls back and re-raises the original
        exception with its traceback when the managed block fails.

        Args:
            exception_class: Exception type raised by the managed block, if any.
            exception_value: Exception raised by the managed block, if any.
            traceback: Traceback associated with ``exception_value``.

        Raises:
            Exception: Re-raises the exception from the managed block after rollback.
        """
        self._is_managing_context = False
        if exception_class is None:
            self.commit()
        else:
            self.rollback()
            raise exception_value.with_traceback(traceback)
