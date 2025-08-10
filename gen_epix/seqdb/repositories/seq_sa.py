from typing import Any
from uuid import UUID

import numpy as np
from sqlalchemy import Engine

from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.fastapp.repositories import SARepository
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository
from gen_epix.seqdb.repositories.sa_model import (
    DB_METADATA_FIELDS,
    GENERATE_SERVICE_METADATA,
    SERVICE_METADATA_FIELDS,
)


class SeqSARepository(SARepository, BaseSeqRepository):
    def __init__(self, engine: Engine, **kwargs: Any):
        entities = kwargs.pop("entities", BaseSeqRepository.ENTITIES)
        super().__init__(
            engine,
            entities=entities,
            service_metadata_fields=SERVICE_METADATA_FIELDS,
            db_metadata_fields=DB_METADATA_FIELDS,
            generate_service_metadata=GENERATE_SERVICE_METADATA,
            **kwargs,
        )

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
