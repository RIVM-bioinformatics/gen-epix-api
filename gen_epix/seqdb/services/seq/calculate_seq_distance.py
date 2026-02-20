import json
from collections.abc import Sequence
from uuid import UUID

from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.domain.service import BaseSeqService


def _calculate_profile_distance(
    profile_type_name: str,
    profile1: Sequence[
        model.SnpProfile | model.AlleleProfile | model.MlvaProfile | model.KmerProfile
    ],
    profile2: Sequence[
        model.SnpProfile | model.AlleleProfile | model.MlvaProfile | model.KmerProfile
    ],
) -> float:
    """Return the distance between two profiles of the same type"""
    if profile_type_name == "snp":
        seq1: str = (
            profile1.aligned_nucleotide_seq  # type: ignore[attr-defined]
            if profile1.aligned_nucleotide_seq  # type: ignore[attr-defined]
            else profile1.snp_profile  # type: ignore[attr-defined]
        )
        seq2: str = (
            profile2.aligned_nucleotide_seq  # type: ignore[attr-defined]
            if profile2.aligned_nucleotide_seq  # type: ignore[attr-defined]
            else profile2.snp_profile  # type: ignore[attr-defined]
        )
        # TODO: check if calculation is ok for SNP profiles
        min_len = min(len(seq1), len(seq2))
        return float(
            sum(1 for i in range(min_len) if seq1[i] != seq2[i])
            + abs(len(seq1) - len(seq2))
        )
    elif profile_type_name == "allele":
        assert isinstance(profile1, model.AlleleProfile)
        assert isinstance(profile2, model.AlleleProfile)
        ids1: list[UUID | None] = profile1.get_allele_ids()
        ids2: list[UUID | None] = profile2.get_allele_ids()
        return float(
            sum(
                1
                for x, y in zip(ids1, ids2)
                if x != y and x is not None and y is not None
            )
        )
    elif profile_type_name == "mlva":
        assert isinstance(profile1, model.MlvaProfile)
        assert isinstance(profile2, model.MlvaProfile)
        # Parse MLVA profiles to get repeat numbers
        if profile1.mlva_profile_format == enum.MlvaProfileFormat.SORTED_REPEAT_NUMBERS:
            repeat_numbers1: list[int] = json.loads(profile1.mlva_profile)
        else:
            raise NotImplementedError("Unsupported MLVA profile format")
        if profile2.mlva_profile_format == enum.MlvaProfileFormat.SORTED_REPEAT_NUMBERS:
            repeat_numbers2: list[int] = json.loads(profile2.mlva_profile)
        else:
            raise NotImplementedError("Unsupported MLVA profile format")
        # Hamming distance: count loci where repeat numbers differ
        # Only count if both repeat numbers are present (not -1)
        return float(
            sum(
                1
                for x, y in zip(repeat_numbers1, repeat_numbers2)
                if x != y
                and x != MLVA_NO_LOCUS_REPEAT_NUMBER
                and y != MLVA_NO_LOCUS_REPEAT_NUMBER
            )
        )
    else:
        return 0.0


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
    user_id = cmd.user.id if cmd.user else None
    results: list[model.CalculateSeqDistancesResult] = []

    # Retrieve all SeqDistanceProtocols
    with self.repository.uow() as uow:
        seq_distance_protocols: list[model.SeqDistanceProtocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.SeqDistanceProtocol,
            None,
            None,
            CrudOperation.READ_ALL,
        )

    # Define profile types with their model classes and matching attributes
    profile_types: list[
        tuple[
            str,
            Sequence[
                model.SnpProfile
                | model.AlleleProfile
                | model.MlvaProfile
                | model.KmerProfile
            ]
            | None,
            type,
        ]
    ] = [
        ("snp", cmd.snp_profiles, model.SnpProfile),
        ("allele", cmd.allele_profiles, model.AlleleProfile),
        ("mlva", cmd.mlva_profiles, model.MlvaProfile),
        ("kmer", cmd.kmer_profiles, model.KmerProfile),
    ]

    for (
        profile_type_name,
        new_profiles,
        profile_model_class,
    ) in profile_types:
        if not new_profiles:
            continue

        if profile_type_name == "kmer":
            raise NotImplementedError("K-mer distance calculation not implemented")

        for protocol in seq_distance_protocols:
            # Determine if protocol applies to this profile type
            applicable = False
            if profile_type_name == "snp" and protocol.ref_seq_id is not None:
                if all(x.ref_seq_id == protocol.ref_seq_id for x in new_profiles):
                    applicable = True
            elif (
                profile_type_name in ["allele", "mlva"]
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
                        profile_type_name,
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
                        profile_type_name,
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
                            status=UploadStatus.UPDATED,
                            seq_distance_profile_id=updated_seq_distance.profile_id,
                        )
                        for updated_seq_distance in modified_existing_seq_distances
                    ]
                )

            # Create all new SeqDistances objects and store them
            new_seq_distances: list[model.SeqDistance] = [
                model.SeqDistance(  # type: ignore[call-arg]
                    id=self.generate_id(),  # type: ignore[arg-type]
                    seq_distance_protocol_id=protocol.id,  # type: ignore[arg-type]
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
                        status=UploadStatus.CREATED,
                        seq_distance_profile_id=created_new_seq_distance.profile_id,  # type : ignore[arg-type]
                    )
                )

    return results
