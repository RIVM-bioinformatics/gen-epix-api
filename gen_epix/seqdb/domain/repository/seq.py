import abc
import json
from collections.abc import Iterable
from typing import Any
from uuid import UUID

import numpy as np

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import enum, exc


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

    @staticmethod
    def _get_matching_profiles_for_distance_dict_format(
        max_distance: float,
        matching_profile_ids: set[UUID],
        distances: str,
        distance_format: enum.SeqDistanceFormat,
    ) -> None:
        if not distances:
            raise exc.InitializationServiceError(
                "Distances field is empty in SeqDistance record"
            )
        if distance_format == enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT:
            try:
                distance_dict = json.loads(distances)
            except json.JSONDecodeError as e:
                raise exc.InitializationServiceError(
                    "Failed to decode distances field in SeqDistance record"
                ) from e
            for profile_id, distance in distance_dict.items():
                if distance <= max_distance:
                    matching_profile_ids.add(profile_id)
