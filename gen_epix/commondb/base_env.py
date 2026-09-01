"""Define the abstract composition contract shared by commondb applications."""

import abc
from collections.abc import Callable
from enum import Enum
from typing import Any

from dynaconf import Dynaconf

from gen_epix.fastapp import App, BaseService
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.fastapp.repository import BaseRepository


class BaseAppComposer(abc.ABC):
    """Define dependencies and repository construction for concrete app composers."""

    def __init__(self) -> None:
        """Initialize abstract composition state placeholders.

        Raises:
            NotImplementedError: Always, because concrete composers must initialize
                application dependencies.
        """
        self._cfg: Dynaconf
        self._app: App
        self._services: dict[Enum, BaseService[Any]]
        self._repositories: dict[Enum, BaseRepository]
        self._registered_user_dependency: Callable
        self._new_user_dependency: Callable
        self._idp_user_dependency: Callable
        raise NotImplementedError()

    @property
    def cfg(self) -> Dynaconf:
        """Return the application's resolved Dynaconf settings."""
        return self._cfg

    @property
    def app(self) -> App:
        """Return the composed FastApp application."""
        return self._app

    @property
    def services(self) -> dict[Enum, BaseService[Any]]:
        """Return services keyed by their service type."""
        return self._services

    @property
    def repositories(self) -> dict[Enum, BaseRepository]:
        """Return repositories keyed by their service type."""
        return self._repositories

    @property
    def registered_user_dependency(self) -> Callable:
        """Return the API dependency that resolves registered users."""
        return self._registered_user_dependency

    @property
    def new_user_dependency(self) -> Callable:
        """Return the API dependency that resolves new users."""
        return self._new_user_dependency

    @property
    def idp_user_dependency(self) -> Callable:
        """Return the API dependency that resolves identity-provider users."""
        return self._idp_user_dependency

    @classmethod
    def create_repository(
        cls,
        service_type: Enum,
        timestamp_factory: Callable,
        entities: list[Entity],
        repository_type: Enum,
        repository_cfg: dict[str, Any],
        repository_class: type[BaseRepository],
        **kwargs: Any,
    ) -> BaseRepository:
        """Create a repository using the configured persistence backend.

        Args:
            cls: Composer class requesting repository construction.
            service_type: Service type that owns the repository.
            timestamp_factory: Factory for persistence timestamps.
            entities: Initial entities passed to the repository.
            repository_type: Configured dictionary, SQLite, or SQL backend type.
            repository_cfg: Backend configuration and connection properties.
            repository_class: Repository implementation class to instantiate.
            **kwargs: Additional backend-specific repository options.

        Returns:
            Initialized repository for the requested backend.

        Raises:
            NotImplementedError: If the configured backend type is unsupported.
        """
        repository: BaseRepository
        props: dict = repository_cfg.get("props", {})
        if repository_type.value == "DICT":
            repository = DictRepository.create_repository_from_pkl(
                repository_class,
                entities,
                props["file"],
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        elif repository_type.value == "SA_SQLITE":
            assert issubclass(repository_class, SARepository)
            file: str | None = props.get("file")
            connection_string: str | None = props.get("connection_string")
            if not connection_string and file:
                connection_string = f"sqlite:///{file}"
            repository = repository_class.create_sa_repository(
                entities,
                connection_string=connection_string,
                name=service_type.value,
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        elif repository_type.value == "SA_SQL":
            assert issubclass(repository_class, SARepository)
            repository = repository_class.create_sa_repository(
                entities,
                connection_string=props["connection_string"],
                name=service_type.value,
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        else:
            raise NotImplementedError()
        return repository
