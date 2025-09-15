from gen_epix.casedb.domain import model as model  # forces models to be registered now
from gen_epix.commondb.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
