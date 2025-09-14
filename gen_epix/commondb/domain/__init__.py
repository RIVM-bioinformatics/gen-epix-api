from gen_epix.commondb.domain.command import COMMANDS_BY_SERVICE_TYPE
from gen_epix.commondb.domain.model import (
    SORTED_MODELS_BY_SERVICE_TYPE,
    SORTED_SERVICE_TYPES,
)
from gen_epix.commondb.util import register_domain_entities
from gen_epix.fastapp import Domain

DOMAIN = Domain("commondb")

register_domain_entities(
    DOMAIN,
    SORTED_SERVICE_TYPES,
    SORTED_MODELS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    COMMANDS_BY_SERVICE_TYPE,  # type: ignore[arg-type]
    set_schema_to_service_type=True,
)
