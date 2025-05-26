from __future__ import annotations

from enum import Enum
from test.test_client.user_journey import UserJourney
from typing import Any, Iterable, Self

import pandas as pd

from gen_epix.casedb.domain import DOMAIN, command


class UserJourneyColumn(Enum):
    TIMESTAMP = "timestamp"
    DURATION = "duration"
    USER_ID = "user_id"
    COMMAND_NAME = "command.class"
    COMMAND_DICT = "command.dict"
    COMMAND_OBJECT = "command.object"


class V2UserJourney(UserJourney):

    def __init__(self, records: pd.DataFrame | Iterable[dict[UserJourneyColumn, Any]]):
        if isinstance(records, pd.DataFrame):
            self.df = records
        else:
            self.df = pd.DataFrame.from_records(records)
        if UserJourneyColumn.COMMAND_OBJECT not in self.df.columns:
            self.df[UserJourneyColumn.COMMAND_OBJECT] = None
            self.set_commands()
        self._has_all_commands = (
            UserJourneyColumn.COMMAND_OBJECT in self.df.columns
            and not self.df[UserJourneyColumn.COMMAND_OBJECT].isnull().any()
        )

    def set_commands(self) -> Self:
        self.df[UserJourneyColumn.COMMAND_OBJECT] = self.df.apply(
            lambda row: self.create_command_from_dict(
                row[UserJourneyColumn.COMMAND_NAME], row[UserJourneyColumn.COMMAND_DICT]
            ),
            axis=1,
        )
        self._has_all_commands = True
        return self

    def get_commands(self, **kwargs: dict) -> pd.DataFrame:
        if not self._has_all_commands:
            self.set_commands()
        return self.df

    def to_pickle(self, path: str, include_commands: bool = False) -> None:
        if not include_commands:
            df = self.df.drop(columns=UserJourneyColumn.COMMAND_OBJECT)
            df[UserJourneyColumn.COMMAND_OBJECT] = None
        else:
            df = self.df
        df.to_pickle(path)

    @classmethod
    def from_pickle(cls, path: str) -> V2UserJourney:
        return cls(pd.read_pickle(path))

    @classmethod
    def create_command_from_dict(
        cls, command_name: str, command_dict: dict
    ) -> command.Command:
        """
        Contains all the logic to convert a command dict to a command obj,
        including logic to convert older formats to current.
        """
        command_class = DOMAIN.get_command_for_name(command_name)
        if issubclass(command_class, command.CrudCommand):
            command_dict.pop("model_class", None)
        return command_class(**command_dict)
