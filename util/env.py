import abc
from typing import Callable, Hashable

from gen_epix.fastapp import App, BaseService
from gen_epix.fastapp.repository import BaseRepository


class BaseAppEnv(abc.ABC):
    def __init__(self) -> None:
        self._cfg: dict
        self._app: App
        self._services: dict[Hashable, BaseService]
        self._repositories: dict[Hashable, BaseRepository]
        self._registered_user_dependency: Callable
        self._new_user_dependency: Callable
        self._idp_user_dependency: Callable
        raise NotImplementedError()

    @property
    def cfg(self) -> dict:
        return self._cfg

    @property
    def app(self) -> App:
        return self._app

    @property
    def services(self) -> dict[Hashable, BaseService]:
        return self._services

    @property
    def repositories(self) -> dict[Hashable, BaseRepository]:
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
