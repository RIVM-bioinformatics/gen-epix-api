from gen_epix.commondb.domain.repository import (
    BaseOrganizationRepository as CommonBaseOrganizationRepository,
)
from gen_epix.seqdb.domain import (
    model as seqdb_model,  # forces models to be registered now
)


class BaseOrganizationRepository(CommonBaseOrganizationRepository):
    pass
