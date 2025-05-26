import gzip
import json
import os
from datetime import datetime
from enum import Enum
from test.test_client.log_parser import AzureColumn, LogCode, LogParser, LogType
from test.test_client.user_journey_v2 import UserJourneyColumn, V2UserJourney
from typing import Callable, Iterable
from uuid import UUID

import pandas as pd

from gen_epix.filter import (
    BooleanOperator,
    CompositeFilter,
    Filter,
    NoFilter,
    RegexFilter,
    StringSetFilter,
)


class SourcePath(Enum):
    TIMESTAMP = ("ts",)
    LOGGER = ("logger",)
    LOG_LEVEL = ("level",)
    CONTENT = ("content",)
    CONTENT_CODE = ("content", "code")
    CONTENT_MESSAGE = ("content", "msg")
    CONTENT_COMMAND_NAME = ("content", "command", "class")
    CONTENT_COMMAND_ID = ("content", "command", "id")
    CONTENT_COMMAND_USER_ID = ("content", "command", "user_id")
    CONTENT_COMMAND_DICT = ("content", "command", "object")
    CONTENT_COMMAND_OPERATION = ("content", "command", "operation")
    CONTENT_COMMAND_PARENT_COMMAND_ID = ("content", "command", "parent_command_id")
    CONTENT_COMMAND_STACK_TRACE = ("content", "command", "stack_trace")
    CONTENT_APP_ID = ("content", "app", "id")
    CONTENT_APP_NAME = ("content", "app", "name")
    CONTENT_SERVICE_ID = ("content", "service", "id")
    CONTENT_SERVICE_NAME = ("content", "service", "name")
    CONTENT_EXCEPTION = ("content", "exception")
    CONTENT_POLICY_CLASS = ("content", "policy", "class")


class Key(Enum):
    TIMESTAMP = "timestamp"
    LOGGER = "logger"
    LOG_LEVEL = "level"
    CODE = "code"
    MESSAGE = "message"
    COMMAND_NAME = "command.class"
    COMMAND_ID = "command.id"
    COMMAND_USER_ID = "command.user_id"
    COMMAND_DICT = "command.object"
    COMMAND_OPERATION = "command.operation"
    COMMAND_PARENT_COMMAND_ID = "command.parent_command_id"
    COMMAND_STACK_TRACE = "command.stack_trace"
    APP_ID = "app.id"
    APP_NAME = "app.name"
    SERVICE_ID = "service.id"
    SERVICE_NAME = "service.name"
    EXCEPTION = "exception"
    POLICY_CLASS = "policy.class"


class KeySet(Enum):
    USER_JOURNEY = {
        Key.TIMESTAMP,
        Key.COMMAND_USER_ID,
        Key.COMMAND_ID,
        Key.COMMAND_NAME,
        Key.COMMAND_DICT,
    }


class V2LogParser(LogParser):

    LOG_LINE_PATTERN: str = r'\{"' + SourcePath.TIMESTAMP.value[0] + r'":'
    LOG_LINE_KEY_MAP_: dict[SourcePath, Key] = {
        SourcePath.TIMESTAMP: Key.TIMESTAMP,
        SourcePath.LOG_LEVEL: Key.LOG_LEVEL,
        SourcePath.LOGGER: Key.LOGGER,
        SourcePath.CONTENT_CODE: Key.CODE,
        SourcePath.CONTENT_MESSAGE: Key.MESSAGE,
        SourcePath.CONTENT_COMMAND_NAME: Key.COMMAND_NAME,
        SourcePath.CONTENT_COMMAND_ID: Key.COMMAND_ID,
        SourcePath.CONTENT_COMMAND_USER_ID: Key.COMMAND_USER_ID,
        SourcePath.CONTENT_COMMAND_DICT: Key.COMMAND_DICT,
        SourcePath.CONTENT_COMMAND_OPERATION: Key.COMMAND_OPERATION,
        SourcePath.CONTENT_COMMAND_PARENT_COMMAND_ID: Key.COMMAND_PARENT_COMMAND_ID,
        SourcePath.CONTENT_COMMAND_STACK_TRACE: Key.COMMAND_STACK_TRACE,
        SourcePath.CONTENT_APP_ID: Key.APP_ID,
        SourcePath.CONTENT_APP_NAME: Key.APP_NAME,
        SourcePath.CONTENT_SERVICE_ID: Key.SERVICE_ID,
        SourcePath.CONTENT_SERVICE_NAME: Key.SERVICE_NAME,
        SourcePath.CONTENT_EXCEPTION: Key.EXCEPTION,
        SourcePath.CONTENT_POLICY_CLASS: Key.POLICY_CLASS,
    }
    LOG_LINE_KEY_MAP: dict[tuple, Key] = {
        x.value: y for x, y in LOG_LINE_KEY_MAP_.items()
    }
    LOG_VALUE_TRANSFORMERS: dict[Key, Callable] = {
        Key.TIMESTAMP: lambda x: None if x is None else datetime.fromisoformat(x),
        Key.COMMAND_ID: lambda x: None if x is None else UUID(x),
        Key.COMMAND_USER_ID: lambda x: None if x is None else UUID(x),
        Key.COMMAND_PARENT_COMMAND_ID: lambda x: None if x is None else UUID(x),
        Key.APP_ID: lambda x: None if x is None else UUID(x),
        Key.SERVICE_ID: lambda x: None if x is None else UUID(x),
    }
    LOG_USER_JOURNEY_COLUMN_MAP: dict[Key, UserJourneyColumn] = {
        Key.TIMESTAMP: UserJourneyColumn.TIMESTAMP,
        Key.COMMAND_USER_ID: UserJourneyColumn.USER_ID,
        Key.COMMAND_NAME: UserJourneyColumn.COMMAND_NAME,
        Key.COMMAND_DICT: UserJourneyColumn.COMMAND_DICT,
    }

    def __init__(self, log_file: str | list[str], log_type: LogType = LogType.DIRECT):
        self.log_files = log_file if isinstance(log_file, list) else [log_file]
        self.log_type = log_type
        self._is_parsed = False
        self.log_records = None
        self.log_error_lines = None
        # Verify existence of log files
        for log_file in self.log_files:
            if not os.path.isfile(log_file):
                raise FileNotFoundError(f"Log file not found: {log_file}")

    def parse(self, **kwargs: dict) -> tuple[list[dict], list[str]]:
        if self._is_parsed:
            raise ValueError("Log already parsed")
        # Get row filter
        filter_log_codes = kwargs.pop("filter_log_codes", [])
        filter_log_codes = (
            filter_log_codes
            if isinstance(filter_log_codes, list)
            else [filter_log_codes]
        )
        filters = []
        if filter_log_codes:
            filters.append(StringSetFilter(key=Key.CODE, members=filter_log_codes))
        if not filters:
            filter = None
        elif len(filters) == 1:
            filter = filters[0]
        else:
            filter = CompositeFilter(filters=filters, operator=BooleanOperator.AND)
        # Filter rows
        records = []
        error_lines = []
        for log_file in self.log_files:
            _, file_extension = os.path.splitext(log_file)
            if self.log_type == LogType.DIRECT:
                with (
                    gzip.open(log_file, "rb")
                    if file_extension.lower() == ".gz"
                    else open(log_file, "rt")
                ) as handle:
                    curr_records, curr_error_lines = V2LogParser._direct_lines_parser(
                        handle, filter
                    )
            elif self.log_type == LogType.AZURE:
                df = pd.read_csv(log_file, compression="infer")
                df = df.rename(
                    columns={x.value: x for x in AzureColumn if x.value in df.columns}
                )
                curr_records, curr_error_lines = V2LogParser._azure_lines_parser(
                    df, filter
                )
            else:
                raise ValueError("Unknown log type")
            records.extend(curr_records)
            error_lines.extend(curr_error_lines)
        self._is_parsed = True
        self.log_records = records
        self.log_error_lines = error_lines
        return records, error_lines

    def create_user_journey(self, **kwargs: dict) -> V2UserJourney:
        # TODO: add filtering, e.g. for a particular user
        add_command = kwargs.get("add_command", False)
        if not self._is_parsed:
            raise ValueError("Log not parsed")
        command_finish_timestamps = {}
        command_record_index = {}
        records = []
        for log_record in self.log_records:
            # Skip records without initial command
            code = log_record.get(Key.CODE)
            if code == LogCode.APP_FINISH.value:
                # Record finish timestamp
                command_finish_timestamps[log_record[Key.COMMAND_ID]] = log_record[
                    Key.TIMESTAMP
                ]
                continue
            if Key.COMMAND_DICT not in log_record:
                continue
            if Key.COMMAND_NAME not in log_record:
                continue
            if (
                Key.COMMAND_PARENT_COMMAND_ID in log_record
                and log_record[Key.COMMAND_PARENT_COMMAND_ID] is not None
            ):
                # Skip child commands
                continue
            if code != LogCode.APP_START.value:
                # Skip non-start service bus commands
                continue
            # Create user journey record, containing the reconstructed command object
            record = {
                V2LogParser.LOG_USER_JOURNEY_COLUMN_MAP[x]: y
                for x, y in log_record.items()
                if x in KeySet.USER_JOURNEY.value
            }
            if add_command:
                record[UserJourneyColumn.COMMAND_OBJECT] = (
                    V2UserJourney.create_command_from_dict(
                        record[UserJourneyColumn.COMMAND_NAME],
                        record[UserJourneyColumn.COMMAND_DICT],
                    )
                )
            if not record.get(UserJourneyColumn.USER_ID):
                user = record.get(UserJourneyColumn.COMMAND_DICT, {}).get("user")
                if user:
                    record[UserJourneyColumn.USER_ID] = user.get("id")
            records.append(record)
            command_record_index[UUID(log_record[Key.COMMAND_DICT]["id"])] = (
                len(records) - 1
            )
        # Add duration to user journey records
        for command_id, finish_timestamp in command_finish_timestamps.items():
            record_index = command_record_index.get(command_id)
            if record_index is not None:
                records[record_index][UserJourneyColumn.DURATION] = (
                    finish_timestamp
                    - records[record_index][UserJourneyColumn.TIMESTAMP]
                )
        return V2UserJourney(records)

    @staticmethod
    def _get_path(record, path):
        value = record.get(path[0])
        if len(path) == 1:
            return value
        for key in path[1:-1]:
            value = value.get(key, {})
        return value.get(path[-1])

    @staticmethod
    def _log_line_to_record(line: str) -> dict[Key | str, str]:
        """
        Convert a log line to a record, mapping SourceKey to Key where possible.
        The nested structure of the log line, with metadata keys and a message key,
        is flattened to a single record. The timestamp is converted to a datetime
        object.
        """
        line_record = json.loads(line)
        record = {
            y: V2LogParser._get_path(line_record, x)
            for x, y in V2LogParser.LOG_LINE_KEY_MAP.items()
            if V2LogParser._get_path(line_record, x) is not None
        }
        content = V2LogParser._get_path(line_record, SourcePath.CONTENT.value)
        if isinstance(content, str):
            record[Key.MESSAGE] = content
        # Transform values
        for value_key, value_transformer in V2LogParser.LOG_VALUE_TRANSFORMERS.items():
            if value_key in record:
                record[value_key] = value_transformer(record[value_key])
        return record

    @staticmethod
    def _direct_lines_parser(
        handle, content_filter: Filter | None
    ) -> tuple[list[dict], list[str]]:
        line_filter = RegexFilter(pattern=V2LogParser.LOG_LINE_PATTERN)
        error_lines = []

        def to_record(lines: Iterable[str]):
            for line in lines:
                try:
                    record = V2LogParser._log_line_to_record(line)
                    yield record
                except json.JSONDecodeError:
                    error_lines.append(line)

        if not content_filter:
            content_filter = NoFilter()
        records = [
            x
            for x in content_filter.filter_rows(
                to_record(line_filter.filter_column(x for x in handle))
            )
        ]
        return records, error_lines

    @staticmethod
    def _azure_lines_parser(
        df: pd.DataFrame, content_filter: Filter | None
    ) -> tuple[list[dict], list[str]]:
        log_string_col_name = LogParser.AZURE_LOG_STRING_COLUMN
        line_filter = RegexFilter(
            key=AzureColumn.CONTENT, pattern=V2LogParser.LOG_LINE_PATTERN
        )
        records = []
        error_lines = []

        def to_merged_record(src_records: Iterable[dict]):
            for src_record in src_records:
                try:
                    content_src_record = src_record.pop(AzureColumn.CONTENT)
                    record = src_record | V2LogParser._log_line_to_record(
                        content_src_record
                    )
                    yield record
                except json.JSONDecodeError:
                    error_lines.append(src_record[AzureColumn.CONTENT])

        if not content_filter:
            content_filter = NoFilter()
        records = [
            x
            for x in content_filter.filter_rows(
                to_merged_record(
                    line_filter.filter_rows(x for x in df.to_dict(orient="records"))
                )
            )
        ]
        return records, error_lines


class LogParser2:
    """
    A class to parse and export logsas produced directly by the application or as stored in Azure Log Analytics Workspace.

    The `LogParser` class reads a log file from a given path, parses the JSON content, and
    handles any errors that might occur during the parsing process. The parsed logs are
    stored in a pandas DataFrame for further analysis and exported for user journey analysis.

    Attributes
    ----------
    df_raw : pd.DataFrame
        DataFrame to store the parsed logs.

    month : str
        Month extracted from the file name.

    path_base : str
        Base path of the log file.

    df_sorted_user_journey : pd.DataFrame
        DataFrame to store the sorted user journey logs.

    Methods
    -------
    parse_log_user_journey
        Parses the log file and sorts the user journey logs.

    export_user_journey
        Exports the sorted user journey logs to a CSV and a pickle file.
    """

    def __init__(self, path: str) -> None:
        self.df_raw = pd.read_csv(path)
        self.month = path.split("_")[-1].split(".")[0]
        self.path_base = path.rsplit("/", 1)[0] + "/"
        self.df_sorted_user_journey: pd.DataFrame | None = None

    def _parse_json(self, json_str: str) -> dict[str, str] | str:

        # the message field sometimes returns HTTP codes,
        # which breaks json.loads() because they dont have ""
        # this is a workaround
        if "'" not in json_str and '"' not in json_str:
            return json_str
        try:
            return json.loads(json_str)  # type: ignore [no-any-return]

        except json.JSONDecodeError:
            try:
                start, end = json_str.split('"message": ')
                end = end[:-1]
                end = '"' + end.replace('"', "") + '"}'
                new_str = start + '"message":' + end
                return json.loads(new_str)  # type: ignore [no-any-return]
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON: {json_str}") from e

    def _flatten_json(self, json_data: str) -> pd.DataFrame:
        # This function is recursive and will flatten nested jsons
        # it takes a long time
        # it also somehow add rows of NaNs to the dfs in the series
        parsed = self._parse_json(json_data)
        mostly_flat = pd.json_normalize(parsed)  # type: ignore [arg-type]

        mask = mostly_flat.apply(lambda x: any(isinstance(i, list) for i in x))
        df_columns_with_lists = mostly_flat.columns[mask]
        df_with_lists = mostly_flat[df_columns_with_lists]

        if df_with_lists.empty:
            return mostly_flat

        final_df_list = []
        for col in df_with_lists.columns:
            column_df_list = [
                self._flatten_json(list_item) for list_item in df_with_lists[col]
            ]
            final_df_list.extend(column_df_list)

        mostly_flat = mostly_flat.drop(columns=df_columns_with_lists)
        flat = pd.concat([mostly_flat] + final_df_list, axis=1)

        return flat

    def _unpack_log_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        series = df["Log_s"]

        series_flat = series.apply(self._flatten_json)  # type: ignore [arg-type]
        series_flat_filtered = series_flat.apply(lambda x: x.dropna(how="all", axis=0))
        df_flat = pd.concat(series_flat_filtered.to_list()).reset_index(drop=True)
        df_final = pd.concat([self.df_raw.reset_index(drop=True), df_flat], axis=1)

        return df_final

    def parse_log_user_journey(self) -> None:
        """
        Parses the log file and sorts the user journey logs.

        This method reads the log file, parses the JSON content, and sorts the logs based on
        the user journey. The sorted logs are stored in the `df_sorted_user_journey` attribute.

        Returns
        -------
        None
        """

        # The login action has a specific action_id
        # There are two different columns with the user id
        ACTION_ID = "982c2866"  # pylint: disable=invalid-name
        EMAIL_COL = "command.content.user.email"  # pylint: disable=invalid-name
        CONTENT_USER_ID_COL = "command.content.user.id"  # pylint: disable=invalid-name
        USER_ID_COL = "command.user_id"  # pylint: disable=invalid-name
        TIMESTAMP_COL = "command.content.timestamp"  # pylint: disable=invalid-name

        df_unpacked = self._unpack_log_to_df(self.df_raw)

        df_unpacked = df_unpacked[df_unpacked["name"] != "app"]
        df_unpacked = df_unpacked.dropna(axis=1, how="all").reset_index()

        # There are two different columns with the user id
        df_emails = df_unpacked[df_unpacked["command.action_id"] == ACTION_ID]
        df_emails_filtered = df_emails[[CONTENT_USER_ID_COL, EMAIL_COL]]
        mapping_dict = df_emails_filtered.set_index(CONTENT_USER_ID_COL).to_dict()[
            EMAIL_COL
        ]
        df_unpacked[EMAIL_COL] = df_unpacked[USER_ID_COL].map(mapping_dict)

        df_user_journey = (
            df_unpacked[df_unpacked[EMAIL_COL].notna()]
            .dropna(axis=1, how="all")
            .reset_index(drop=True)
        )

        df_user_journey = df_user_journey.drop(
            columns=[
                "index",
                "TenantId",
                "SourceSystem",
                "ContainerId_g",
                "ContainerImage_s",
                "Category",
                "Stream_s",
                "time_d",
                "_timestamp_d",
                "EnvironmentName_s",
                "ContainerGroupName_s",
                "ContainerName_s",
                "ContainerGroupId_g",
                "Log_s",
                "RevisionName_s",
                "ContainerAppName_s",
                "Type",
                "command.content.software_version",
            ],
            axis=1,
        )

        # group by user_id and sort those groups by timestamp
        df_user_journey = df_user_journey.sort_values(TIMESTAMP_COL)
        df_user_journey["sort_user_id_groups"] = df_user_journey.groupby(USER_ID_COL)[
            TIMESTAMP_COL
        ].transform("first")

        # within the same user_id group, sort by timestamp
        # cant find a way to do both these groupbys in one
        df_user_journey = (
            df_user_journey.groupby(USER_ID_COL)
            .apply(lambda x: x.sort_values(TIMESTAMP_COL))
            .reset_index(drop=True)
        )

        # sort_values normally uses quicksort, but this is not stable
        # it loses the order of the rows when the values are the same
        # so the order within the same "sort_user_id_groups" is lost
        # to keep the order, we use mergesort
        self.df_sorted_user_journey = (
            df_user_journey.sort_values("sort_user_id_groups", kind="mergesort")
            .drop(columns=["sort_user_id_groups"], axis=1)
            .reset_index(drop=True, inplace=True)
        )

    def export_user_journey(self) -> None:
        """
        Exports the sorted user journey logs to a CSV and a pickle file.

        This method takes the sorted user journey logs stored in the `df_sorted_user_journey`
        attribute and exports them to a CSV file and a pickle file in the base path directory.

        Returns
        -------
        None
        """
        if not self.df_sorted_user_journey:
            raise ValueError("No user journey to export")

        self.df_sorted_user_journey.to_csv(
            f"{self.path_base}user_journey_{self.month}.csv", index=False
        )
        self.df_sorted_user_journey.to_pickle(
            f"{self.path_base}user_journey_{self.month}.pkl"
        )


if __name__ == "__main__":
    log_parser = V2LogParser("data/logs/ContainerAppConsoleLogs_CL_April.csv")
    log_parser.parse_log_user_journey()
    log_parser.export_user_journey()
