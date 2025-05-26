import abc
from enum import Enum
from test.test_client.user_journey import UserJourney

import pandas as pd


class LogCode(Enum):
    APP_START = "e94cad9b"
    APP_FINISH = "5ab6c248"


class LogType(Enum):
    DIRECT = "DIRECT"
    AZURE = "AZURE"


class AzureColumn(Enum):
    # Azure specific
    CONTENT = "Log_s"
    INDEX = "index"
    TENANT_ID = "TenantId"
    SOURCE_SYSTEM = "SourceSystem"
    CONTAINER_ID = "ContainerId_g"
    CONTAINER_IMAGE = "ContainerImage_s"
    CATEGORY = "Category"
    STREAM = "Stream_s"
    TIME = "time_t [UTC]"
    TIME_GENERATED = "TimeGenerated [UTC]"
    TIMESTAMP = "_timestamp_d"
    ENVIRONMENT_NAME = "EnvironmentName_s"
    CONTAINER_GROUP_NAME = "ContainerGroupName_s"
    CONTAINER_NAME = "ContainerName_s"
    CONTAINER_GROUP_ID = "ContainerGroupId_g"
    REVISION_NAME = "RevisionName_s"
    CONTAINER_APP_NAME = "ContainerAppName_s"
    TYPE = "Type"
    COMMAND_CONTENT_SOFTWARE_VERSION = "command.content.software_version"


class LogParser(abc.ABC):
    # Azure specific

    def __init__(self, log_type: LogType):
        self.log_type = log_type
        self.log_records: list[dict] = []

    @abc.abstractmethod
    def parse(self, **kwargs: dict) -> tuple[list[dict], list[str]]:
        raise NotImplementedError

    def to_excel(self, path: str) -> None:
        df = pd.DataFrame.from_records(self.log_records)
        df.to_excel(path, index=False)

    @abc.abstractmethod
    def create_user_journey(self, **kwargs: dict) -> UserJourney:
        raise NotImplementedError
