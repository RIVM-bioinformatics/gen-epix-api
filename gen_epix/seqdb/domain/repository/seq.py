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
        """Retrieve UUIDs of profiles similar to specified profiles."""
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
        profile_ids: list[UUID] | None = None,
    ) -> Iterable[model.SeqDistance]:
        """Iterate over SeqDistance records for a protocol.

        When ``profile_ids`` is given, only records whose
        ``seq_profile_id`` is in that list are yielded.
        When ``None``, all records for the protocol are yielded
        """
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
    def get_profiles_without_seq_distance(
        self,
        uow: BaseUnitOfWork,
        distance_protocol_id: UUID,
        seq_profile_protocol_ids: list[UUID],
        limit: int | None = None,
    ) -> list[model.SeqProfile]:
        """Return profiles that have no SeqDistance record for
        distance_protocol_id.

        Pushes the set-difference into SQL (NOT EXISTS subquery) so that
        neither the full profile list nor the full distance-profile-id set
        is materialised in Python.  limit is applied as a SQL LIMIT /
        TOP so only the required rows are transferred.
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
    def update_some_seq_distance_content(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        objs: list[model.SeqDistance],
    ) -> None:
        """Update only the content field of SeqDistance records in bulk.

        Exists as a domain-specific method rather than relying on the
        framework's UPDATE_SOME because UPDATE_SOME issues one ORM flush
        per row (474 round trips for a typical production call). This
        method issues a single Core executemany statement instead.

        Option B — modifying the framework's update_some to use bulk
        updates — was deliberately not chosen: update_some does a
        read-then-write cycle (fetch ORM rows → apply mapper → flush)
        that handles modified_at via onupdate and modified_by via the
        mapper. A bulk Core UPDATE bypasses both, so it cannot be a
        transparent drop-in without risking silent side-effect omissions
        for other callers across all four services.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_profiles_from_pairs(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
        profile_ids: list[UUID],
        max_distance: float,
        **kwargs: Any,
    ) -> list[UUID]:
        """Query seq_distance_pair for profiles within max_distance of any of
        profile_ids. Returns matching profile IDs excluding the input IDs."""
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
