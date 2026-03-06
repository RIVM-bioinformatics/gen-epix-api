from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import enum, exc, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository


class SeqDictRepository(DictRepository, BaseSeqRepository):

    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        self.raise_on_duplicate_ids(seq_ids)

        seqs: list[model.Seq] = self.read_some(model.Seq, seq_ids)  # type: ignore[assignment]
        for seq in seqs:
            assert seq.id is not None
            contig_list: list[tuple[UUID, str]] = []
            for contig in seq.contigs:
                if contig.seq_format != enum.SeqFormat.STR_DNA:
                    raise exc.InitializationServiceError(
                        f"FASTA export not supported for {contig.seq_format.value} format"
                    )
                assert contig.id is not None
                contig_list.append((contig.id, contig.seq))
            yield (seq.id, contig_list)

    def retrieve_similar_profiles(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        if not profile_ids:
            return []

        profile_id_set = set(profile_ids)
        table: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
            model.SeqDistance
        ]
        matching_profile_ids: set[UUID] = set()
        for seq_distance in table.values():
            if seq_distance.seq_distance_protocol_id != seq_distance_protocol_id:
                continue
            if seq_distance.profile_id not in profile_id_set:
                continue
            # Each seq_distance corresponds to one profile_id
            # distances is a stringified dict: {other_profile_id: distance}
            distances: str = seq_distance.distances
            distance_format: enum.SeqDistanceFormat = seq_distance.distance_format
            # shared logic to parse distances for dict format in BaseSeqRepository
            BaseSeqRepository._get_matching_profiles_for_distance_dict_format(
                max_distance, matching_profile_ids, distances, distance_format
            )

        return list(matching_profile_ids - profile_id_set)

    def iter_seq_distances(
        self,
        uow: BaseUnitOfWork,
        seq_distance_protocol_id: UUID,
    ) -> Iterable[model.SeqDistance]:
        table: dict[UUID, model.SeqDistance] = self.db[  # type: ignore[assignment]
            model.SeqDistance
        ]
        for seq_distance in table.values():
            if seq_distance.seq_distance_protocol_id == seq_distance_protocol_id:
                yield seq_distance
