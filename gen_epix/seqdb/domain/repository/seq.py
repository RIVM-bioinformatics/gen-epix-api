import abc
from uuid import UUID

import numpy as np

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model as model  # forces models to be registered now


class BaseSeqRepository(BaseRepository):
    pass

    @abc.abstractmethod
    def get_distance_matrix_by_seq_ids(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        seq_ids: list[UUID],
    ) -> np.ndarray:
        raise NotImplementedError
