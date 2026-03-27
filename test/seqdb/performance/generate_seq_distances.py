import base64
import hashlib
import uuid
from test.seqdb.seqdb_test_client import (
    DistanceMatrix,
    SeqdbTestClient,
    SeqGenerationSettings,
)
from typing import Any
from uuid import UUID

import pandas as pd

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import enum, model


def create_seq_distance_database(
    n_loci: int = 5, n_seqs: int = 10
) -> dict[type, dict[UUID, Any]]:

    sample_batch_for_upload = get_random_sequences(n_loci, n_seqs)
    locus_set = get_locus_set(n_loci)
    protocol = get_locus_detection_protocol()
    data_collection = get_data_collection()
    sample = get_sample(data_collection)
    seqs = get_seqs(sample_batch_for_upload, sample)
    allele_profiles = get_allele_profiles(
        sample_batch_for_upload, sample, locus_set, protocol, seqs
    )
    protocol = get_seq_distance_protocol(locus_set)
    profile_ids = get_allele_profile_ids(allele_profiles)
    distance_matrix = SeqdbTestClient.calculate_distance_matrix_from_allele_profiles(
        allele_profiles
    )
    seq_distances = get_seq_distances(
        allele_profiles, sample, protocol, profile_ids, distance_matrix
    )

    # create a 'dict' repository from the demo models as dict[class/model] = {instance.id: instance}
    db: dict[type, dict[UUID, Any]] = {}
    db[model.LocusSet] = {locus_set.id: locus_set}  # type: ignore[dict-item]
    db[model.Protocol] = {protocol.id: protocol}  # type: ignore[dict-item]
    db[model.DataCollection] = {data_collection.id: data_collection}  # type: ignore[dict-item]
    db[model.Sample] = {sample.id: sample}  # type: ignore[dict-item]
    db[model.Protocol] = {protocol.id: protocol}  # type: ignore[dict-item]
    db[model.Seq] = {x.id: x for x in seqs}  # type: ignore[misc]
    db[model.SeqProfile] = {x.id: x for x in allele_profiles}  # type: ignore[misc]
    db[model.SeqDistance] = {x.seq_profile_id: x for x in seq_distances}

    return db


def get_seq_distances(
    allele_profiles: list[model.SeqProfile],
    sample: model.Sample,
    protocol: model.Protocol,
    profile_ids: list[UUID],
    distance_matrix: DistanceMatrix,
) -> list[model.SeqDistance]:
    seq_distances: list[model.SeqDistance] = []
    n = len(profile_ids)
    for i in range(n):
        distances_dict: dict[str, float] = {}
        for j in range(n):
            pid_j = profile_ids[j]
            distances_dict[str(pid_j)] = float(distance_matrix.matrix[i][j])
        seq_distance = model.SeqDistance(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            sample_id=sample.id,
            protocol_id=protocol.id,  # type: ignore[arg-type]
            seq_profile_id=profile_ids[i],
            format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            content=pd.Series(distances_dict).to_json(),
        )
        seq_distances.append(seq_distance)
    return seq_distances


def get_allele_profile_ids(allele_profiles: list[model.SeqProfile]) -> list[UUID]:
    profile_ids: list[UUID] = []
    for allele_profile in allele_profiles:
        if allele_profile.id is None:
            allele_profile.id = uuid.uuid4()
        profile_ids.append(allele_profile.id)
    assert len(profile_ids) == len(allele_profiles)
    return profile_ids


def get_seq_distance_protocol(locus_set: model.LocusSet) -> model.Protocol:
    seq_distance_protocol = model.Protocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="ALLELE_HAMMING_TEST",
        name="Allele Hamming Test",
        is_integer_distance=True,
        protocol_type=enum.ProtocolType.SEQ_DISTANCE,
        seq_distance_type=enum.SeqDistanceType.ALLELE_HAMMING,
        locus_set_id=locus_set.id,
        max_stored_distance=1e6,
    )

    return seq_distance_protocol


def get_data_collection() -> model.DataCollection:
    data_collection = model.DataCollection(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="DC_TEST",
        name="Data Collection Test",
    )

    return data_collection


def get_sample(data_collection: model.DataCollection) -> model.Sample:
    sample = model.Sample(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="SAMPLE_TEST",
        created_in_data_collection_id=data_collection.id,  # type: ignore[arg-type]
    )

    return sample


def get_locus_detection_protocol() -> model.Protocol:
    locus_detection_protocol = model.Protocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="LDP_TEST",
        name="Locus Detection Protocol Test",
        protocol_type=enum.ProtocolType.LOCUS_PROFILE,
    )

    return locus_detection_protocol


def get_locus_set(n_loci: int) -> model.LocusSet:
    locus_set = model.LocusSet(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="LS_TEST",
        name="Locus Set Test",
        n_loci=n_loci,
        locus_ids=[uuid.uuid4() for _ in range(n_loci)],
    )

    return locus_set


def get_allele_profiles(
    sample_batch_for_upload: model.SampleBatchForUpload,
    sample: model.Sample,
    locus_set: model.LocusSet,
    protocol: model.Protocol,
    seqs: list[model.Seq],
) -> list[model.SeqProfile]:
    allele_profiles: list[model.SeqProfile] = []
    samples_for_upload: list[model.SampleForUpload] = sample_batch_for_upload.samples
    seq_idx = 0
    for sample_for_upload in samples_for_upload:
        for allele_profile_for_upload in sample_for_upload.allele_profiles:  # type: ignore[union-attr]
            sorted_allele_ids = sorted(
                allele_profile_for_upload.allele_ids, key=lambda x: x or NULL_ID  # type: ignore[arg-type]
            )
            allele_bytes_list: list[bytes] = [
                (allele_id.bytes if allele_id else NULL_ID.bytes)
                for allele_id in sorted_allele_ids
            ]
            allele_profile_bytes = b"".join(allele_bytes_list)
            allele_profile_str = base64.b64encode(allele_profile_bytes).decode("ascii")
            sha256 = hashlib.sha256()
            sha256.update(allele_profile_bytes)
            allele_profile_hash = UUID(sha256.digest()[:16].hex())
            n_loci = sum(
                1  # type: ignore[misc]
                for allele_id in allele_profile_for_upload.allele_ids  # type: ignore[union-attr]
                if (allele_id is not None and allele_id != NULL_ID)
            )

            allele_profile = model.SeqProfile(  # type: ignore[call-arg]
                sample_id=sample.id,
                seq_id=seqs[seq_idx].id,
                locus_set_id=locus_set.id,
                protocol_id=protocol.id,  # type: ignore[arg-type]
                n_loci=n_loci,
                allele_profile=allele_profile_str,
                allele_profile_format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
                allele_profile_hash=allele_profile_hash,
            )
            allele_profiles.append(allele_profile)
            seq_idx += 1

    return allele_profiles


def get_seqs(
    sample_batch_for_upload: model.SampleBatchForUpload, sample: model.Sample
) -> list[model.Seq]:
    seqs: list[model.Seq] = []
    for sample_for_upload in sample_batch_for_upload.samples:
        for seq_for_upload in sample_for_upload.seqs:  # type: ignore[union-attr]
            seq = model.Seq(  # type: ignore[call-arg]
                id=uuid.uuid4(),
                sample_id=sample.id,
                code="SEQ_TEST_" + str(uuid.uuid4()),
                contigs=[
                    model.Contig(
                        seq=seq_for_upload.contigs[0].seq,
                        seq_format=seq_for_upload.contigs[0].seq_format,
                        length=seq_for_upload.contigs[0].length,
                    )
                ],
            )
            seqs.append(seq)
    return seqs


def get_random_sequences(n_loci: int, n_seqs: int) -> model.SampleBatchForUpload:
    settings = SeqGenerationSettings(
        n_loci=n_loci,
        locus_length=50,
        p_locus_deletion=0,
        p_nucleotide_substitution=0.002,
        p_nucleotide_deletion=0.0005,
        seed=1001,
    )
    batch = SeqdbTestClient.generate_random_sequences(n_seqs=n_seqs, settings=settings)
    return batch
