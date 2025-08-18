from gen_epix.common.domain.repository import (
    BaseOrganizationRepository as CommonBaseOrganizationRepository,
)
from gen_epix.seqdb.domain import model as model  # forces models to be registered now


class BaseOrganizationRepository(CommonBaseOrganizationRepository):
    pass
