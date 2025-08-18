from gen_epix.common.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)
from gen_epix.seqdb.domain import model as model  # forces models to be registered now


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
