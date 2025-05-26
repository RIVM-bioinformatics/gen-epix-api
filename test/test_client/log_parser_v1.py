import gzip
import json
import os
from datetime import datetime
from enum import Enum
from test.test_client.log_parser import AzureColumn, LogCode, LogParser, LogType
from test.test_client.user_journey_v1 import UserJourneyColumn, V1UserJourney
from typing import Iterable

import pandas as pd

from gen_epix.filter import (
    BooleanOperator,
    CompositeFilter,
    Filter,
    NoFilter,
    RegexFilter,
    StringSetFilter,
)


class LogSourceKey(Enum):
    TIMESTAMP = "ts"
    LOG_LEVEL = "level"
    LOGGER = "name"
    MESSAGE = "message"
    ACTION_ID = "action_id"
    COMMAND_TYPE = "command_name"
    COMMAND_ID = "command_id"
    COMMAND = "command"
    STATUS = "status"
    USER_ID = "user_id"
    PARENT_COMMAND_ID = "parent_command_id"
    APP_ID = "app_id"
    STACK_TRACE = "stack_trace"
    EXCEPTION = "exception"


class LogKey(Enum):
    TIMESTAMP = "timestamp"
    LOG_LEVEL = "log_level"
    LOGGER = "logger"
    MESSAGE = "message"
    ACTION_ID = "action_id"
    COMMAND_TYPE = "command_name"
    COMMAND_ID = "command_id"
    COMMAND = "command"
    STATUS = "status"
    USER_ID = "user_id"
    PARENT_COMMAND_ID = "parent_command_id"
    APP_ID = "app_id"
    STACK_TRACE = "stack_trace"
    EXCEPTION = "exception"


class LogKeySet(Enum):
    METADATA = {LogKey.TIMESTAMP, LogKey.LOG_LEVEL, LogKey.LOGGER}
    DATA = {
        LogKey.ACTION_ID,
        LogKey.COMMAND_TYPE,
        LogKey.COMMAND_ID,
        LogKey.COMMAND,
        LogKey.STATUS,
        LogKey.USER_ID,
        LogKey.PARENT_COMMAND_ID,
        LogKey.APP_ID,
        LogKey.STACK_TRACE,
        LogKey.EXCEPTION,
    }
    USER_JOURNEY = {
        LogKey.TIMESTAMP,
        LogKey.USER_ID,
        LogKey.COMMAND_TYPE,
        LogKey.COMMAND,
    }


class V1LogParser(LogParser):

    LOG_LINE_PATTERN: str = r'\{"' + LogSourceKey.TIMESTAMP.value + r'":'
    LOG_LINE_METADATA_KEY_MAP: dict[str, LogKey] = {
        LogSourceKey.TIMESTAMP.value: LogKey.TIMESTAMP,
        LogSourceKey.LOG_LEVEL.value: LogKey.LOG_LEVEL,
        LogSourceKey.LOGGER.value: LogKey.LOGGER,
    }
    LOG_LINE_DATA_KEY_MAP: dict[str, LogKey] = {
        LogSourceKey.ACTION_ID.value: LogKey.ACTION_ID,
        LogSourceKey.COMMAND_TYPE.value: LogKey.COMMAND_TYPE,
        LogSourceKey.COMMAND_ID.value: LogKey.COMMAND_ID,
        LogSourceKey.COMMAND.value: LogKey.COMMAND,
        LogSourceKey.STATUS.value: LogKey.STATUS,
        LogSourceKey.USER_ID.value: LogKey.USER_ID,
        LogSourceKey.PARENT_COMMAND_ID.value: LogKey.PARENT_COMMAND_ID,
        LogSourceKey.APP_ID.value: LogKey.APP_ID,
        LogSourceKey.STACK_TRACE.value: LogKey.STACK_TRACE,
        LogSourceKey.EXCEPTION.value: LogKey.EXCEPTION,
    }
    LOG_USER_JOURNEY_COLUMN_MAP: dict[LogKey, UserJourneyColumn] = {
        LogKey.TIMESTAMP: UserJourneyColumn.TIMESTAMP,
        LogKey.USER_ID: UserJourneyColumn.USER_ID,
        LogKey.COMMAND_TYPE: UserJourneyColumn.COMMAND_TYPE,
        LogKey.COMMAND: UserJourneyColumn.COMMAND_DICT,
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
        filter_action_ids = kwargs.pop("filter_action_ids", [])
        filter_action_ids = (
            filter_action_ids
            if isinstance(filter_action_ids, list)
            else [filter_action_ids]
        )
        filters = []
        if filter_action_ids:
            filters.append(
                StringSetFilter(
                    key=LogSourceKey.ACTION_ID.value, members=filter_action_ids
                )
            )
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
                    gzip.open(log_file, "rt")
                    if file_extension.lower() == ".gz"
                    else open(log_file, "rt")
                ) as handle:
                    curr_records, curr_error_lines = V1LogParser._direct_lines_parser(
                        handle, filter
                    )
            elif self.log_type == LogType.AZURE:
                df = pd.read_csv(log_file, compression="infer")
                df = df.rename(
                    columns={x.value: x for x in AzureColumn if x.value in df.columns}
                )
                curr_records, curr_error_lines = V1LogParser._azure_lines_parser(
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

    def create_user_journey(self, **kwargs: dict) -> V1UserJourney:
        # TODO: add filtering, e.g. for a particular user
        add_command = kwargs.get("add_command", False)
        if not self._is_parsed:
            raise ValueError("Log not parsed")
        command_finish_timestamps = {}
        command_record_index = {}
        records = []
        for log_record in self.log_records:
            # Skip records without initial command
            action_id = log_record.get(LogKey.ACTION_ID)
            if action_id == LogCode.APP_FINISH.value:
                # Record finish timestamp
                command_finish_timestamps[log_record[LogKey.COMMAND_ID]] = log_record[
                    LogKey.TIMESTAMP
                ]
                continue
            if LogKey.COMMAND not in log_record:
                continue
            if LogKey.COMMAND_TYPE not in log_record:
                continue
            if (
                LogKey.PARENT_COMMAND_ID in log_record
                and log_record[LogKey.PARENT_COMMAND_ID] is not None
            ):
                # Skip child commands
                continue
            if action_id != LogCode.APP_START.value:
                # Skip non-start service bus commands
                continue
            # Create user journey record, containing the reconstructed command object
            record = {
                V1LogParser.LOG_USER_JOURNEY_COLUMN_MAP[x]: y
                for x, y in log_record.items()
                if x in LogKeySet.USER_JOURNEY.value
            }
            if add_command:
                record[UserJourneyColumn.COMMAND_OBJECT] = (
                    V1UserJourney.create_command_from_dict(
                        record[UserJourneyColumn.COMMAND_TYPE],
                        record[UserJourneyColumn.COMMAND_DICT],
                    )
                )
            if not record.get(UserJourneyColumn.USER_ID):
                user = record.get(UserJourneyColumn.COMMAND_DICT, {}).get("user")
                if user:
                    record[UserJourneyColumn.USER_ID] = user.id
            records.append(record)
            command_record_index[log_record[LogKey.COMMAND_ID]] = len(records) - 1
        # Add duration to user journey records
        for command_id, finish_timestamp in command_finish_timestamps.items():
            record_index = command_record_index.get(command_id)
            if record_index is not None:
                records[record_index][UserJourneyColumn.DURATION] = (
                    finish_timestamp
                    - records[record_index][UserJourneyColumn.TIMESTAMP]
                )
        return V1UserJourney(records)

    @staticmethod
    def _log_line_to_record(line: str) -> dict[LogKey | str, str]:
        """
        Convert a log line to a record, mapping SourceLogKey to LogKey where possible.
        The nested structure of the log line, with metadata keys and a message key,
        is flattened to a single record. The timestamp is converted to a datetime
        object.
        """
        line_record = json.loads(line)
        record = {
            y: line_record[x] for x, y in V1LogParser.LOG_LINE_METADATA_KEY_MAP.items()
        }
        record[LogKey.TIMESTAMP] = datetime.fromisoformat(record[LogKey.TIMESTAMP])
        message = line_record.get(LogSourceKey.MESSAGE.value)
        if isinstance(message, str):
            record[LogSourceKey.MESSAGE] = message
        else:
            record.update(
                {
                    V1LogParser.LOG_LINE_DATA_KEY_MAP.get(x, x): y
                    for x, y in message.items()
                }
            )
        return record

    @staticmethod
    def _direct_lines_parser(
        handle, content_filter: Filter | None
    ) -> tuple[list[dict], list[str]]:
        line_filter = RegexFilter(pattern=V1LogParser.LOG_LINE_PATTERN)
        error_lines = []

        def to_record(lines: Iterable[str]):
            for line in lines:
                try:
                    record = V1LogParser._log_line_to_record(line)
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
        line_filter = RegexFilter(
            key=AzureColumn.CONTENT, pattern=V1LogParser.LOG_LINE_PATTERN
        )
        records = []
        error_lines = []

        def to_merged_record(src_records: Iterable[dict]):
            for src_record in src_records:
                try:
                    content_src_record = src_record.pop(AzureColumn.CONTENT)
                    record = src_record | V1LogParser._log_line_to_record(
                        content_src_record
                    )
                    yield record
                except json.JSONDecodeError:
                    error_lines.append(content_src_record)

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
