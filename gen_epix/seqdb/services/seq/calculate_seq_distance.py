import json
from collections.abc import Sequence
from uuid import UUID

from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_calculate_seq_distances_for_new_profiles(
    self: BaseSeqService,
    cmd: command.CalculateSeqDistancesForNewProfilesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    TODO: Implement the actual distance calculation logic here.
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
            str | None,
        ]
    ] = [
        ("snp", cmd.snp_profiles, model.SnpProfile, "ref_seq_id"),
        ("allele", cmd.allele_profiles, model.AlleleProfile, "locus_set_id"),
        ("mlva", cmd.mlva_profiles, model.MlvaProfile, "locus_set_id"),
        ("kmer", cmd.kmer_profiles, model.KmerProfile, None),
    ]

    for (
        profile_type_name,
        new_profiles,
        profile_model_class,
        match_attribute,
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

            # Initialize distance maps for new profiles
            new_profile_distance_maps: dict[UUID, dict[str, float]] = {
                x.id: {} for x in new_profiles if x.id is not None
            }

            # Retrieve existing profile distances and profile data
            with self.repository.uow() as uow:
                existing_seq_distances: list[model.SeqDistance] = list(
                    self.repository.iter_seq_distances(uow, protocol.id)
                )

                # Retrieve existing profiles (batch read to avoid N DB calls)
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
                    x.id: x  # type: ignore[misc]
                    for x in existing_profiles_list
                    if getattr(x, "id", None) is not None
                }

            # Process existing profiles and calculate distances
            modified_existing_seq_distances: list[model.SeqDistance] = []
            for existing_seq_distance in existing_seq_distances:
                existing_profile = existing_profiles[existing_seq_distance.profile_id]
                existing_distance_map = json.loads(existing_seq_distance.distances)
                modified = False

                for new_profile in new_profiles:
                    # Calculate distance inline based on profile type
                    if profile_type_name == "snp":
                        # SNP: count positions where base differs
                        seq1: str = (
                            existing_profile.aligned_nucleotide_seq  # type: ignore[union-attr]
                            if existing_profile.aligned_nucleotide_seq  # type: ignore[union-attr]
                            else existing_profile.snp_profile  # type: ignore[union-attr]
                        )
                        seq2: str = (
                            new_profile.aligned_nucleotide_seq  # type: ignore[union-attr]
                            if new_profile.aligned_nucleotide_seq  # type: ignore[union-attr]
                            else new_profile.snp_profile  # type: ignore[union-attr]
                        )
                        # TODO: check if calculation is ok for SNP profiles
                        min_len = min(len(seq1), len(seq2))
                        distance = sum(1 for i in range(min_len) if seq1[i] != seq2[i])
                        distance += abs(len(seq1) - len(seq2))
                    elif profile_type_name == "allele":
                        assert isinstance(existing_profile, model.AlleleProfile)
                        ids1: list[UUID | None] = existing_profile.get_allele_ids()
                        ids2: list[UUID | None] = new_profile.get_allele_ids()  # type: ignore[union-attr]
                        # Hamming distance: count loci where alleles differ
                        # Only count if both alleles are present (not None)
                        distance: float = float(
                            sum(
                                1
                                for x, y in zip(ids1, ids2)
                                if x != y and x is not None and y is not None
                            )
                        )
                    elif profile_type_name == "mlva":
                        assert isinstance(existing_profile, model.MlvaProfile)
                        assert isinstance(new_profile, model.MlvaProfile)
                        # Parse MLVA profiles to get repeat numbers
                        if (
                            existing_profile.mlva_profile_format
                            == enum.MlvaProfileFormat.SORTED_REPEAT_NUMBERS
                        ):
                            repeat_numbers1: list[int] = json.loads(
                                existing_profile.mlva_profile
                            )
                        else:
                            raise NotImplementedError("Unsupported MLVA profile format")

                        if (
                            new_profile.mlva_profile_format
                            == enum.MlvaProfileFormat.SORTED_REPEAT_NUMBERS
                        ):
                            repeat_numbers2: list[int] = json.loads(
                                new_profile.mlva_profile
                            )
                        else:
                            raise NotImplementedError("Unsupported MLVA profile format")

                        # Hamming distance: count loci where repeat numbers differ
                        # Only count if both repeat numbers are present (not -1)
                        distance: float = float(
                            sum(
                                1
                                for x, y in zip(repeat_numbers1, repeat_numbers2)
                                if x != y
                                and x != MLVA_NO_LOCUS_REPEAT_NUMBER
                                and y != MLVA_NO_LOCUS_REPEAT_NUMBER
                            )
                        )
                    else:
                        distance: float = 0.0

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

            # Batch update modified existing SeqDistances
            with self.repository.uow() as uow:
                self.repository.crud(
                    uow,
                    user_id,
                    model.SeqDistance,
                    modified_existing_seq_distances,
                    None,
                    CrudOperation.UPDATE_SOME,
                )

            # Create new SeqDistances
            with self.repository.uow() as uow:
                for new_profile in new_profiles:
                    new_seq_distance = model.SeqDistance(
                        id=self.generate_id(),
                        seq_distance_protocol_id=protocol.id,
                        profile_id=new_profile.id,
                        sample_id=new_profile.sample_id,
                        distance_format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
                        distances=json.dumps(new_profile_distance_maps[new_profile.id]),
                    )
                    self.repository.crud(
                        uow,
                        user_id,
                        model.SeqDistance,
                        new_seq_distance,
                        None,
                        CrudOperation.CREATE_ONE,
                    )

            # Create results after successful SeqDistance creation
            for new_profile in new_profiles:
                results.append(
                    model.CalculateSeqDistancesResult(
                        id=new_profile.id,
                        status=UploadStatus.CREATED,
                        seq_distance_profile_id=new_profile.id,
                    )
                )

    return results
