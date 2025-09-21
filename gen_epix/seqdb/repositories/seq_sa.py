from typing import Iterable, Tuple
from uuid import UUID

import numpy as np
import sqlalchemy as sa

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.repositories import sa_model


class SeqSARepository(SARepository, BaseSeqRepository):

    def get_distance_matrix_by_seq_ids(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        seq_ids: list[UUID],
    ) -> np.ndarray:
        raise NotImplementedError("Code to be converted to seqdb architecture")
        self.raise_on_duplicate_ids(seq_ids)
        seqs = self.crud(
            uow,
            None,
            model.SeqDistance,
            None,
            seq_ids,
            CrudOperation.READ_SOME,
        )
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
        assert isinstance(uow, SAUnitOfWork)
        stmt = (
            sa.select(sa_model.Seq.id, sa_model.RawSeq.seq)
            .join(sa_model.RawSeq, sa_model.Seq.raw_seq_id == sa_model.RawSeq.id)
            .where(sa_model.Seq.id.in_(seq_ids))
        )

        result = uow.session.execute(stmt)
        for seq_id, raw_seq in result:
            print(f"Yielding seq_id={seq_id} with raw_seq length={len(raw_seq)}")
            yield (seq_id, raw_seq)
