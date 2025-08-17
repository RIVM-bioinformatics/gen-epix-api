from gen_epix.common.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)
from gen_epix.omopdb.domain import model as model  # forces models to be registered now


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
