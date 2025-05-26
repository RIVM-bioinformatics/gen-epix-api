from __future__ import annotations

import abc

import pandas as pd

from gen_epix.casedb.domain import command


class UserJourney(abc.ABC):
    @abc.abstractmethod
    def get_commands(self, **kwargs: dict) -> pd.DataFrame:
        raise NotImplementedError

    @abc.abstractmethod
    def to_pickle(self, path: str, include_commands: bool = False) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_pickle(cls, path: str) -> UserJourney:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create_command_from_dict(
        cls, command_name: str, command_dict: dict
    ) -> command.Command:
        raise NotImplementedError
