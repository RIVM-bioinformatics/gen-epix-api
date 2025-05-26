# Perhaps there's a better location for this?
# Also best practice might be rename all enum.py files enums.py to ensure avoiding name collisions with built-in enum module.

from enum import Enum


class AnonStrictness(Enum):
    IGNORE = "ignore"
    WARN = "warn"
    STRICT = "strict"


class AnonMethod(Enum):
    MAKE_NULL = "make_null"
    SHIFT = "shift"
    RANDOM = "random"
    CATEGORICAL = "categorical"
    MODEL_ANONYIMIZATION = "model_anonymization"  # for future use
