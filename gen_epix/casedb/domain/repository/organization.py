from gen_epix.casedb.domain import model as model  # forces models to be registered now
from gen_epix.common.domain.repository import (
    BaseOrganizationRepository as CommonBaseOrganizationRepository,
)


class BaseOrganizationRepository(CommonBaseOrganizationRepository):
    pass
