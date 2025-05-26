from gen_epix.omopdb.domain import DOMAIN, enum
from gen_epix.omopdb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.omopdb.repositories.sa_model.organization import *
from util.util import set_entity_repository_model_classes

FIELD_NAME_MAP: dict[Type, dict[str, str]] = {}

set_entity_repository_model_classes(
    DOMAIN,
    enum.ServiceType,
    RowMetadataMixin,
    "gen_epix.omopdb.repositories.sa_model",
    field_name_map=FIELD_NAME_MAP,
)
