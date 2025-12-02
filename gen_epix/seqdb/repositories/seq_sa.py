from collections.abc import Iterable
from uuid import UUID

import numpy as np
import sqlalchemy as sa

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
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
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        self.raise_on_duplicate_ids(seq_ids)
        assert isinstance(uow, SAUnitOfWork)
        mapper = self.get_mapper(model.Seq)
        stmt = sa.select(sa_model.Seq).where(sa_model.Seq.id.in_(seq_ids))
        result = uow.session.execute(stmt)
        for sa_seq in result:
            seq: model.Seq = mapper.load(sa_seq)  # type: ignore[assignment]
            contig_list = []
            for contig in seq.contigs:
                if contig.seq_format != enum.SeqFormat.STR_DNA:
                    raise exc.InitializationServiceError(
                        f"FASTA export not supported for {contig.seq_format.value} format"
                    )
                contig_list.append((contig.seq_hash, contig.seq))
            yield (seq.id, contig_list)
