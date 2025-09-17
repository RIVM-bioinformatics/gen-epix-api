from gen_epix.casedb.domain.command import COMMANDS_BY_SERVICE_TYPE, COMMON_COMMAND_MAP
from gen_epix.casedb.domain.model import (
    COMMON_MODEL_IMPL,
    SORTED_MODELS_BY_SERVICE_TYPE,
    SORTED_SERVICE_TYPES,
)
from gen_epix.commondb.util import register_domain_entities
from gen_epix.fastapp import Domain

DOMAIN = Domain("casedb")

register_domain_entities(
    DOMAIN,
    SORTED_SERVICE_TYPES,
    SORTED_MODELS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    COMMANDS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    common_model_map=COMMON_MODEL_IMPL,
    common_command_map=COMMON_COMMAND_MAP,
    set_schema_to_service_type=True,
)
