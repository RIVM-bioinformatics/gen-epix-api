from collections.abc import Iterable
from typing import Any
from uuid import UUID

import numpy as np

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import (
    CompositeFilter,
    EqualsUuidFilter,
    LogicalOperator,
    UuidSetFilter,
)
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import enum, exc, model
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
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        self.raise_on_duplicate_ids(seq_ids)

        seqs: list[model.Seq] = self.read_some(model.Seq, seq_ids)  # type: ignore[assignment]
        for seq in seqs:
            assert seq.id is not None
            contig_list = []
            for contig in seq.contigs:
                if contig.seq_format != enum.SeqFormat.STR_DNA:
                    raise exc.InitializationServiceError(
                        f"FASTA export not supported for {contig.seq_format.value} format"
                    )
                contig_list.append((contig.id, contig.seq))
            yield (seq.id, contig_list)

    def get_similar_profiles(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        if not profile_ids:
            return []

        filter_protocol = EqualsUuidFilter(
            key="seq_distance_protocol_id", value=seq_distance_protocol_id
        )
        filter_profiles = UuidSetFilter(
            key="profile_id", members=frozenset(profile_ids)
        )
        seq_distances: list[model.SeqDistance] = self.read_all(  # type: ignore[assignment]
            model.SeqDistance,
            filter=CompositeFilter(
                filters=[filter_protocol, filter_profiles],
                operator=LogicalOperator.AND,
            ),
        )

        matching_profile_ids: set[UUID] = set()
        for seq_distance in seq_distances:
            # Each seq_distance corresponds to one profile_id
            # distances is a stringified dict: {other_profile_id: distance}
            distances: str = seq_distance.distances
            distance_format: enum.SeqDistanceFormat = seq_distance.distance_format
            # shared logic to parse distances for dict format in BaseSeqRepository
            BaseSeqRepository._get_matching_profiles_for_distance_dict_format(
                max_distance, matching_profile_ids, distances, distance_format
            )

        return list(matching_profile_ids)
