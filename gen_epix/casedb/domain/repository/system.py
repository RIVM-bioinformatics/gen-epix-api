from gen_epix.casedb.domain import model as model  # forces models to be registered now
from gen_epix.common.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
