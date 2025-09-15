import datetime
import uuid
from enum import Enum

import ulid


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now()


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid
