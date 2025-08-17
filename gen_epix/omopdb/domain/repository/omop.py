from gen_epix.fastapp import BaseRepository
from gen_epix.omopdb.domain import model as model  # forces models to be registered now


class BaseOmopRepository(BaseRepository):
    pass
