import abc
import json
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import enum, model


class BaseSeqRepository(BaseRepository):

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
    def retrieve_similar_profiles(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        raise NotImplementedError()

    @staticmethod
    def _get_matching_profiles_for_distance_dict_format(
        max_distance: float,
        matching_profile_ids: set[UUID],
        distance_format: enum.SeqDistanceFormat,
        distances: str,
        distances2: str | None = None,
    ) -> None:
        if distance_format == enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP:
            distance_dict = json.loads(distances)
            for profile_id, distance in distance_dict.items():
                if distance <= max_distance:
                    matching_profile_ids.add(UUID(profile_id))

    @abc.abstractmethod
    def iter_seq_distances(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[model.SeqDistance]:
        raise NotImplementedError()
