import abc
from collections.abc import Iterable
from typing import Any
from uuid import UUID

import numpy as np

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class BaseSeqRepository(BaseRepository):

    @abc.abstractmethod
    def get_distance_matrix_by_seq_ids(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        seq_ids: list[UUID],
    ) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        """
        Retrieve an Iterable[tuple[seq_id, list[tuple[contig_hash, contig_seq]]]] that
        can be converted into FASTA format through a streaming approach.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_similar_profiles(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
        ) -> list[UUID]:
        raise NotImplementedError()
