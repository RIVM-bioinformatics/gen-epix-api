from gen_epix.casedb.domain import DOMAIN, enum
from gen_epix.casedb.repositories.sa_model.organization import User as User
from gen_epix.casedb.repositories.sa_model.organization import (
    UserInvitation as UserInvitation,
)
from gen_epix.common.repositories.sa_model import (
    RowMetadataMixin,
    create_field_metadata,
    set_entity_repository_model_classes,
)

set_entity_repository_model_classes(
    DOMAIN, enum.ServiceType, RowMetadataMixin, "gen_epix.casedb.repositories.sa_model"
)

SERVICE_METADATA_FIELDS, DB_METADATA_FIELDS, GENERATE_SERVICE_METADATA = (
    create_field_metadata(DOMAIN)
)
