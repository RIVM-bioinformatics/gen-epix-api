from gen_epix.commondb.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)
from gen_epix.seqdb.domain import (
    model as seqdb_model,  # forces models to be registered now
)


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
