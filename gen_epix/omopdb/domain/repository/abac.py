from gen_epix.commondb.domain.repository import (
    BaseAbacRepository as CommonBaseAbacRepository,
)
from gen_epix.seqdb.domain import model as model  # forces models to be registered now


class BaseAbacRepository(CommonBaseAbacRepository):
    pass
