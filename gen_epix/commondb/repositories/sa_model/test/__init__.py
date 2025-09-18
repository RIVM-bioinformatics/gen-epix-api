from gen_epix.commondb.domain import DOMAIN, enum
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.test.organization import User as User
from gen_epix.commondb.repositories.sa_model.test.organization import (
    UserInvitation as UserInvitation,
)
from gen_epix.commondb.repositories.sa_model.util import (
    create_field_metadata,
    set_entity_repository_model_classes,
)

set_entity_repository_model_classes(
    DOMAIN,
    enum.ServiceType,
    RowMetadataMixin,
    "gen_epix.seqdb.repositories.sa_model.test",
)

SERVICE_METADATA_FIELDS, DB_METADATA_FIELDS, GENERATE_SERVICE_METADATA = (
    create_field_metadata(DOMAIN)
)
