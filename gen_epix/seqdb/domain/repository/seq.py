import abc
import json
from collections.abc import Iterable
from collections.abc import Set as AbstractSet
from datetime import datetime
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

    @abc.abstractmethod
    def iter_seq_distance_profile_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[UUID]:
        """
        Yield unique profile IDs that have SeqDistance
        records for the given protocol.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_max_seq_distance_modified_at(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> datetime | None:
        """
        Return the maximum modified_at timestamp of
        SeqDistance records for the given protocol.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_profiles_by_protocol_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_ids: list[UUID],
    ) -> list[model.SeqProfile]:
        """
        Return all SeqProfiles linked to the given
        profiling protocol IDs.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_sample_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        """
        Retrieve sample IDs for samples and sample-linked data modified in the
        [modified_since, modified_until) range.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_full_samples_by_sample_ids(
        self,
        sample_ids: list[UUID],
    ) -> list[model.FullSample]:
        """
        Retrieve all relevant data for the specified sample IDs and construct
        FullSample objects.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def filter_seq_profiles_by_quality(
        self,
        uow: BaseUnitOfWork,
        seq_profile_ids: list[UUID],
        allowed_qc_results: AbstractSet[
            enum.QualityControlResult
        ] = enum.QualityControlResultSet.USABLE.value,
    ) -> list[UUID]:
        """
        Given a list of SeqProfile IDs, return the subset of SeqProfiles IDs
        that have a usable quality check result.
        """
        raise NotImplementedError()
