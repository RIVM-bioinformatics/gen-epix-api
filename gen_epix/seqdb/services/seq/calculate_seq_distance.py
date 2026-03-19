import json
from collections.abc import Sequence
from uuid import UUID

import numpy as np

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.service import BaseSeqService


def _calculate_profile_distance(
    profile_model_class: (
        type[model.SnpProfile]
        | type[model.AlleleProfile]
        | type[model.MlvaProfile]
        | type[model.KmerProfile]
    ),
    profile1: Sequence[
        model.SnpProfile | model.AlleleProfile | model.MlvaProfile | model.KmerProfile
    ],
    profile2: Sequence[
        model.SnpProfile | model.AlleleProfile | model.MlvaProfile | model.KmerProfile
    ],
    ref_seq: model.RefSeq | None = None,
    locus_set: model.LocusSet | None = None,
) -> float:
    """Return the distance between two profiles of the same type"""
    if profile_model_class == model.SnpProfile:
        assert isinstance(profile1, model.SnpProfile)
        assert isinstance(profile2, model.SnpProfile)
        # TODO: this implementation is not correct as the aligned sequences may contain different gaps in the reference sequence between both. Instead, the differences versus the reference sequence should be enumerated and compared.
        seq1 = profile1.get_aligned_nucleotide_seq(ref_seq=ref_seq)
        seq2 = profile2.get_aligned_nucleotide_seq(ref_seq=ref_seq)
        return float(np.count_nonzero(np.array(list(seq1)) != np.array(list(seq2))))
    elif profile_model_class == model.AlleleProfile:
        assert isinstance(profile1, model.AlleleProfile)
        assert isinstance(profile2, model.AlleleProfile)
        ids1: list[UUID | None] = profile1.get_allele_ids(locus_set=locus_set)
        ids2: list[UUID | None] = profile2.get_allele_ids(locus_set=locus_set)
        return float(
            sum(
                1
                for x, y in zip(ids1, ids2)
                if x != y and x is not None and y is not None
            )
        )
    elif profile_model_class == model.MlvaProfile:
        assert isinstance(profile1, model.MlvaProfile)
        assert isinstance(profile2, model.MlvaProfile)
        # Parse MLVA profiles to get repeat numbers
        repeat_numbers1 = profile1.get_repeat_numbers(locus_set=locus_set)
        repeat_numbers2 = profile2.get_repeat_numbers(locus_set=locus_set)
        # Hamming distance: count loci where repeat numbers differ
        # Only count if both repeat numbers are present (not -1)
        return float(sum(1 for x, y in zip(repeat_numbers1, repeat_numbers2) if x != y))
    else:
        raise NotImplementedError(
            f"Distance calculation not implemented for {profile_model_class.__name__}"
        )


def seq_service_calculate_seq_distances_for_new_profiles(
    self: BaseSeqService,
    cmd: command.CalculateSeqDistancesForNewProfilesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    Method that takes batches of profiles (SNP, allele, MLVA — k‑mer not implemented) and finds which SeqDistanceProtocols apply.
    For each applicable protocol it computes distances between every new profile and existing stored profiles and
    between new profiles themselves using type-specific distance rules. It updates any modified existing SeqDistance records,
    creates SeqDistance records for the new profiles, and returns a list of results describing the created distance records.
    """

    # TODO: to be refactored to lower both memory and computational complexity

    user_id = cmd.user.id if cmd.user else None
    results: list[model.CalculateSeqDistancesResult] = []

    # Retrieve all Protocols
    with self.repository.uow() as uow:
        protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            None,
            None,
            CrudOperation.READ_ALL,
        )

    # filter protocols by type
    protocols = [
        protocol
        for protocol in protocols
        if protocol.protocol_type == enum.ProtocolType.SEQ_DISTANCE
    ]

    # Define profile types with their model classes and matching attributes
    profile_data: list[
        tuple[
            type,
            Sequence[
                model.SnpProfile
                | model.AlleleProfile
                | model.MlvaProfile
                | model.KmerProfile
            ]
            | None,
        ]
    ] = [
        (model.SnpProfile, cmd.snp_profiles),
        (model.AlleleProfile, cmd.allele_profiles),
        (model.MlvaProfile, cmd.mlva_profiles),
        (model.KmerProfile, cmd.kmer_profiles),
    ]

    for (
        profile_model_class,
        new_profiles,
    ) in profile_data:
        if not new_profiles:
            continue

        if profile_model_class == model.KmerProfile:
            raise NotImplementedError("K-mer distance calculation not implemented")

        for protocol in protocols:
            # Determine if protocol applies to this profile type
            applicable = False
            if profile_model_class == model.SnpProfile:
                assert protocol.ref_seq_id is not None
                if all(x.ref_seq_id == protocol.ref_seq_id for x in new_profiles):
                    applicable = True
            elif (
                profile_model_class in [model.AlleleProfile, model.MlvaProfile]
                and protocol.locus_set_id is not None
            ):
                if all(x.locus_set_id == protocol.locus_set_id for x in new_profiles):
                    applicable = True

            if not applicable:
                continue

            # Initialize distance maps for new profiles.
            new_profiles_list = [x for x in new_profiles if x.id is not None]
            new_profile_distance_maps: dict[UUID, dict[str, float]] = {
                x.id: {} for x in new_profiles_list  # type: ignore[misc]
            }

            # Retrieve existing SeqDistances (for protocol) and profiles
            with self.repository.uow() as uow:
                # TODO: instead of reading all SeqDistances in memory first, stream through them and calculate
                existing_seq_distances: list[model.SeqDistance] = list(
                    self.repository.iter_seq_distances(uow, protocol.id)  # type: ignore[attr-defined]
                )

                # Retrieve existing profiles from db based on profile_ids in existing_seq_distances
                existing_profile_ids: list[UUID] = list(
                    dict.fromkeys(x.profile_id for x in existing_seq_distances)
                )
                existing_profiles_list = (
                    self.repository.crud(
                        uow,
                        user_id,
                        profile_model_class,
                        None,
                        existing_profile_ids,
                        CrudOperation.READ_SOME,
                    )
                    if existing_profile_ids
                    else []
                )
                existing_profiles: dict[
                    UUID,
                    model.SnpProfile
                    | model.AlleleProfile
                    | model.MlvaProfile
                    | model.KmerProfile,
                ] = {
                    x.id: x  # type: ignore[union-attr,misc]
                    for x in existing_profiles_list  # type: ignore[union-attr]
                    if getattr(x, "id", None) is not None
                }

            # Calculate distances of every existing profile against every new profile
            modified_existing_seq_distances: list[model.SeqDistance] = []
            for existing_seq_distance in existing_seq_distances:
                existing_profile = existing_profiles[existing_seq_distance.profile_id]
                existing_distance_map = json.loads(existing_seq_distance.distances)
                modified = False
                for new_profile in new_profiles_list:
                    distance = _calculate_profile_distance(
                        profile_model_class,
                        existing_profile,
                        new_profile,
                    )
                    if distance <= protocol.max_stored_distance:
                        # Update existing profile's distance map with new profile
                        existing_distance_map[str(new_profile.id)] = distance
                        # Update new profile's distance map with existing profile
                        new_profile_distance_maps[new_profile.id][
                            str(existing_profile.id)
                        ] = distance
                        modified = True

                if modified:
                    existing_seq_distance.distances = json.dumps(existing_distance_map)
                    modified_existing_seq_distances.append(existing_seq_distance)

            # Calculate distances of new profiles against each other profile (inter-batch pairs)
            for i in range(len(new_profiles_list)):
                for j in range(i + 1, len(new_profiles_list)):
                    n_i = new_profiles_list[i]
                    n_j = new_profiles_list[j]
                    distance = _calculate_profile_distance(
                        profile_model_class,
                        n_i,
                        n_j,
                    )
                    if distance <= protocol.max_stored_distance:
                        new_profile_distance_maps[n_i.id][str(n_j.id)] = distance  # type: ignore[index]
                        new_profile_distance_maps[n_j.id][str(n_i.id)] = distance  # type: ignore[index]

            # Update modified existing SeqDistances
            if modified_existing_seq_distances:
                with self.repository.uow() as uow:
                    self.repository.crud(
                        uow,
                        user_id,
                        model.SeqDistance,
                        modified_existing_seq_distances,
                        None,
                        CrudOperation.UPDATE_SOME,
                    )
                results.extend(
                    [
                        model.CalculateSeqDistancesResult(
                            id=updated_seq_distance.id,
                            status=EtlStatus.UPDATED,
                            seq_distance_profile_id=updated_seq_distance.profile_id,
                        )
                        for updated_seq_distance in modified_existing_seq_distances
                    ]
                )

            # Create all new SeqDistances objects and store them
            new_seq_distances: list[model.SeqDistance] = [
                model.SeqDistance(  # type: ignore[call-arg]
                    id=self.generate_id(),  # type: ignore[arg-type]
                    protocol_id=protocol.id,  # type: ignore[arg-type]
                    profile_id=new_profile.id,  # type: ignore[arg-type]
                    sample_id=new_profile.sample_id,
                    distance_format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
                    distances=json.dumps(new_profile_distance_maps[new_profile.id]),
                )
                for new_profile in new_profiles_list
            ]
            with self.repository.uow() as uow:
                created_new_seq_distances: list[model.SeqDistance] = self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    model.SeqDistance,
                    new_seq_distances,
                    None,
                    CrudOperation.CREATE_SOME,
                )

            # Create results for created SeqDistances
            for created_new_seq_distance in created_new_seq_distances:
                results.append(
                    model.CalculateSeqDistancesResult(
                        id=created_new_seq_distance.id,
                        status=EtlStatus.CREATED,
                        seq_distance_profile_id=created_new_seq_distance.profile_id,  # type : ignore[arg-type]
                    )
                )

    return results
