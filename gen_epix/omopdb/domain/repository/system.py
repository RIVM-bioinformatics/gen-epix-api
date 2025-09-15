from gen_epix.commondb.domain.repository import (
    BaseSystemRepository as CommonBaseSystemRepository,
)
from gen_epix.omopdb.domain import model as model  # forces models to be registered now


class BaseSystemRepository(CommonBaseSystemRepository):
    pass
