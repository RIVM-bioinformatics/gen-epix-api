from uuid import UUID

import numpy as np

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository


class SeqDictRepository(DictRepository, BaseSeqRepository):
    def get_distance_matrix_by_seq_ids(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        seq_ids: list[UUID],
    ) -> np.ndarray:
        raise NotImplementedError("Code to be converted to seqdb architecture")
        self.raise_on_duplicate_ids(seq_ids)
        seqs = self.read_some(model.SeqDistance, seq_ids)
        id_to_idx_map = {x.id: i for i, x in enumerate(seqs)}
        n = len(seqs)
        distance_matrix = np.empty((n, n))
        distance_matrix[:] = np.nan
        for i in range(n):
            for id_, distance in seqs[i].distances.items():
                if id_ not in id_to_idx_map:
                    continue
                distance_matrix[id_to_idx_map[id_], i] = distance
            distance_matrix[i, i] = 0
        return distance_matrix
