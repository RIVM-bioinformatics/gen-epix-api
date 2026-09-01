"""Define seqdb domain interfaces and policies for domain.repository.seq."""

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
    """Define backend-independent persistence operations for seqdb sequence data."""

    @abc.abstractmethod
    def retrieve_seq_fasta(
        self,
        uow: BaseUnitOfWork,
        seq_ids: list[UUID],
    ) -> Iterable[tuple[UUID, list[tuple[UUID, str]]]]:
        """Stream sequence and contig data for FASTA generation.

        Args:
            uow: Unit of work used for persistence access.
            seq_ids: Sequence identifiers to retrieve.

        Returns:
            Sequence identifiers paired with their contig hashes and nucleotide strings.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
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
        """Return profiles within a distance threshold of the supplied profiles.

        Args:
            uow: Unit of work used for persistence access.
            protocol_id: Distance protocol to query.
            profile_ids: Source profile identifiers.
            max_distance: Inclusive distance threshold.
            **kwargs: Backend-specific query options.

        Returns:
            Matching profile identifiers.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @staticmethod
    def _get_matching_profiles_for_distance_dict_format(
        max_distance: float,
        matching_profile_ids: set[UUID],
        distance_format: enum.SeqDistanceFormat,
        distances: str,
        distances2: str | None = None,
    ) -> None:
        """Add distance-map profiles no farther than the supplied threshold."""
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
        """Iterate sequence-distance records for a protocol.

        Args:
            uow: Unit of work used for persistence access.
            protocol_id: Distance protocol to query.
            profile_ids: Optional profile IDs to limit yielded records.

        Returns:
            Matching sequence-distance records.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def iter_seq_distance_profile_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> Iterable[UUID]:
        """Yield profile identifiers having distance records for a protocol.

        Args:
            uow: Unit of work used for persistence access.
            protocol_id: Distance protocol to query.

        Returns:
            Unique profile identifiers with stored distances.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_max_seq_distance_modified_at(
        self,
        uow: BaseUnitOfWork,
        protocol_id: UUID,
    ) -> datetime | None:
        """Return the latest distance-record modification time for a protocol.

        Args:
            uow: Unit of work used for persistence access.
            protocol_id: Distance protocol to query.

        Returns:
            Latest modification time, or ``None`` when no records exist.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_profiles_by_protocol_ids(
        self,
        uow: BaseUnitOfWork,
        protocol_ids: list[UUID],
    ) -> list[model.SeqProfile]:
        """Return profiles linked to any supplied profiling protocol.

        Args:
            uow: Unit of work used for persistence access.
            protocol_ids: Profiling protocol identifiers.

        Returns:
            Matching sequence profiles.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
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
        """Return profiles lacking a record for a distance protocol.

        Args:
            uow: Unit of work used for persistence access.
            distance_protocol_id: Distance protocol whose records must be absent.
            seq_profile_protocol_ids: Profiling protocols to search.
            limit: Maximum number of profiles to return.

        Returns:
            Profiles without a stored distance record.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_sample_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        """Return samples modified directly or through linked data in a time range.

        Args:
            uow: Unit of work used for persistence access.
            modified_since: Inclusive modification-time lower bound.
            modified_until: Exclusive modification-time upper bound.

        Returns:
            Matching sample identifiers.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_full_samples_by_sample_ids(
        self,
        sample_ids: list[UUID],
    ) -> list[model.FullSample]:
        """Construct complete sample aggregates for the supplied identifiers.

        Args:
            sample_ids: Samples to retrieve with their linked data.

        Returns:
            Complete sample aggregates.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
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

        Args:
            uow: Unit of work used for persistence access.
            user_id: User to record as the modifier, when applicable.
            objs: Distance records whose content is updated.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
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
        """Return profile IDs whose quality result is in the allowed set.

        Args:
            uow: Unit of work used for persistence access.
            seq_profile_ids: Profiles to filter.
            allowed_qc_results: Quality results considered usable.

        Returns:
            Profile IDs with an allowed quality result.

        Raises:
            NotImplementedError: Always, until a concrete repository implements it.
        """
        raise NotImplementedError()
