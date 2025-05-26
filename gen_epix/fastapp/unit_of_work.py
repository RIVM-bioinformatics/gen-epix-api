import abc
from types import TracebackType
from typing import Self, Type


class BaseUnitOfWork(abc.ABC):
    def __init__(self) -> None:
        self._is_managing_context: bool = False

    @property
    def is_managing_context(self) -> bool:
        return self._is_managing_context

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError()

    def flush(self) -> None:
        pass

    def __enter__(self) -> Self:
        self._is_managing_context = True
        return self

    def __exit__(
        self,
        exception_class: Type[Exception] | None,
        exception_value: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        self._is_managing_context = False
        if exception_class is None:
            self.commit()
        else:
            self.rollback()
            raise exception_class(exception_value).with_traceback(traceback)
