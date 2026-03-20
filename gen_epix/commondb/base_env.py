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
    def __init__(self) -> None:
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
        return self._cfg

    @property
    def app(self) -> App:
        return self._app

    @property
    def services(self) -> dict[Enum, BaseService[Any]]:
        return self._services

    @property
    def repositories(self) -> dict[Enum, BaseRepository]:
        return self._repositories

    @property
    def registered_user_dependency(self) -> Callable:
        return self._registered_user_dependency

    @property
    def new_user_dependency(self) -> Callable:
        return self._new_user_dependency

    @property
    def idp_user_dependency(self) -> Callable:
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
        repository: BaseRepository
        if repository_type.value == "DICT":
            repository = DictRepository.create_repository_from_pkl(
                repository_class,
                entities,
                repository_cfg["props"]["file"],
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        elif repository_type.value == "SA_SQLITE":
            assert issubclass(repository_class, SARepository)
            repository = repository_class.create_sa_repository(
                entities,
                "sqlite:///" + repository_cfg["props"]["file"],
                name=service_type.value,
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        elif repository_type.value == "SA_SQL":
            assert issubclass(repository_class, SARepository)
            repository = repository_class.create_sa_repository(
                entities,
                repository_cfg["props"]["connection_string"],
                name=service_type.value,
                timestamp_factory=timestamp_factory,
                **kwargs,
            )
        else:
            raise NotImplementedError()
        return repository
