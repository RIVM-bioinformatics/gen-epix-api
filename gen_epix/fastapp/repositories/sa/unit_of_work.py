from types import TracebackType
from typing import Self, Type

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import Session

from gen_epix.fastapp import exc
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class SAUnitOfWork(BaseUnitOfWork):
    """
    Unit of work class wrapping the SQLAlchemy session.

    The context stack that can be passed during construction indicates whether work
    would be executed within another unit of work's context. If so, that context will
    be responsible for committing or rolling back the session and this unit of work will
    not commit or rollback on exit when used as a context manager. This avoids creating
    nested sessions.
    """

    def __init__(
        self, session: Session, context_stack: list[BaseUnitOfWork] | None = None
    ):
        super().__init__()
        self._session = session
        self._context_stack = context_stack

    @property
    def session(self) -> Session:
        return self._session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def flush(self) -> None:
        self._session.flush()

    @staticmethod
    def _handle_exception(
        exception_class: Type[Exception],
        exception_value: Exception,
        traceback: TracebackType | None,
    ) -> Exception:
        """
        Handle exceptions raised during a unit of work, converting them into a domain
        exception when they are due to normal operation such as a unique constraint
        failing. Any other exceptions are re-raised with traceback.
        """
        if issubclass(exception_class, exc.DomainException):
            raise exception_value
        if issubclass(exception_class, AttributeError):
            raise exception_value
        if issubclass(exception_class, PydanticValidationError):
            raise ValueError(
                f"Model validation error: {str(exception_value)}"
            ).with_traceback(traceback)
        if issubclass(exception_class, sa_exc.IntegrityError):
            if "UNIQUE" in str(exception_value).upper():
                raise exc.UniqueConstraintViolationError(
                    f"Unique constraint violation: {str(exception_value)}",
                )
            elif "NOT NULL" in str(exception_value).upper():
                raise exc.NotNullConstraintViolationError(
                    f"Not null constraint violation: {str(exception_value)}",
                )
            elif "FOREIGN KEY" in str(exception_value).upper():
                raise exc.LinkConstraintViolationError(
                    f"Foreign key constraint violation: {str(exception_value)}",
                )
            else:
                raise NotImplementedError().with_traceback(traceback)
        if issubclass(exception_class, sa_exc.StatementError):
            raise ValueError(f"Statement error: {str(exception_value)}").with_traceback(
                traceback
            )
        raise NotImplementedError().with_traceback(traceback)

    def __enter__(self) -> Self:
        if self._context_stack is not None:
            self._context_stack.append(self)
        self._is_managing_context = True
        return self

    def __exit__(
        self,
        exception_class: Type[Exception] | None,
        exception_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        self._is_managing_context = False
        # Handle nested contexts
        if self._context_stack is not None:
            # Remove self from stack
            assert self._context_stack[-1] is self
            self._context_stack.pop()
            # Check if nested context
            if self._context_stack:
                # Nested context since stack is not empty -> do not commit or rollback,
                # let the outer context handle it instead
                return
        # Commit or rollback based on exception
        if exception_class is None:
            try:
                self.commit()
            except Exception as exception:
                self.rollback()
                # Propagate exception
                SAUnitOfWork._handle_exception(
                    type(exception), exception, exception.__traceback__
                )
        else:
            self.rollback()
            # Propagate exception
            SAUnitOfWork._handle_exception(exception_class, exception_value, traceback)  # type: ignore[arg-type]
