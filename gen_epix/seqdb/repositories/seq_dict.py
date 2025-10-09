from collections.abc import Iterable
from typing import Tuple
from uuid import UUID

import numpy as np

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.repository import BaseSeqRepository


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

    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[str, str]]:
        self.raise_on_duplicate_ids(seq_ids)

        for seq_id in seq_ids:
            seq: model.Seq = self.read_one(model.Seq, seq_id)  # type: ignore[assignment]
            raw_seq: model.RawSeq = self.read_one(  # type: ignore[assignment]
                model.RawSeq,
                seq.raw_seq_id,
            )
            yield (seq.id, raw_seq.seq)  # type: ignore[misc]
