from gen_epix.commondb.domain.repository import (
    BaseAbacRepository as CommonBaseAbacRepository,
)
from gen_epix.seqdb.domain import (
    model as seqdb_model,  # forces models to be registered now
)


class BaseAbacRepository(CommonBaseAbacRepository):
    pass
