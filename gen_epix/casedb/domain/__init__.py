import sys

from gen_epix.casedb.domain.command import COMMANDS_BY_SERVICE_TYPE, COMMON_COMMAND_MAP
from gen_epix.casedb.domain.model import (
    COMMON_MODEL_MAP,
    SORTED_MODELS_BY_SERVICE_TYPE,
    SORTED_SERVICE_TYPES,
)
from gen_epix.commondb.domain.util import register_domain_entities
from gen_epix.fastapp import Domain

DOMAIN = Domain("casedb")

_TESTING = "pytest" in sys.modules

register_domain_entities(
    DOMAIN,
    SORTED_SERVICE_TYPES,
    SORTED_MODELS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    COMMANDS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    common_model_map=COMMON_MODEL_MAP,
    common_command_map=COMMON_COMMAND_MAP,
    # set_schema_to_service_type=not _TESTING,
    set_schema_to_service_type=True,
)
