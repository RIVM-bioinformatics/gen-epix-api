from gen_epix.common.util import register_domain_entities
from gen_epix.fastapp import Domain
from gen_epix.seqdb.domain.command import COMMANDS_BY_SERVICE_TYPE, COMMON_COMMAND_IMPL
from gen_epix.seqdb.domain.model import (
    COMMON_MODEL_IMPL,
    SORTED_MODELS_BY_SERVICE_TYPE,
    SORTED_SERVICE_TYPES,
)

DOMAIN = Domain("seqdb")

register_domain_entities(
    DOMAIN,
    SORTED_SERVICE_TYPES,
    SORTED_MODELS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    COMMANDS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    common_model_impl=COMMON_MODEL_IMPL,
    common_command_impl=COMMON_COMMAND_IMPL,
)
