import datetime
from uuid import UUID

NULL_ID = UUID("00000000-0000-0000-0000-000000000000")

MIN_DATETIME = datetime.datetime(1, 1, 1, 0, 0, 0)
MAX_DATETIME = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

MAX_CODE_FIELD_LENGTH = 255
