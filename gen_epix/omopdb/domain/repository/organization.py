from gen_epix.common.domain.repository import (
    BaseOrganizationRepository as CommonBaseOrganizationRepository,
)
from gen_epix.omopdb.domain import model as model  # forces models to be registered now


class BaseOrganizationRepository(CommonBaseOrganizationRepository):
    pass
