import uuid
from test.seqdb.seqdb_test_client import DistanceMatrix
from test.seqdb.seqdb_test_client import SeqdbTestClient
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.seqdb.seqdb_test_client import SeqGenerationSettings
from typing import Any
from uuid import UUID

import pandas as pd

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import enum, model

import base64
import hashlib

def create_seq_distance_database(
    env: Env, n_loci: int = 5, n_seqs: int = 10
) -> dict[type, dict[UUID, Any]]:
    sample_batch_for_upload = get_random_sequences(n_loci, n_seqs)
    allele_profiles = convert_allele_profile_for_upload(sample_batch_for_upload)
    locus_set = get_locus_set(n_loci)
    locus_detection_protocol = get_locus_detection_protocol()
    data_collection = get_data_collection()
    sample = get_sample(data_collection)

    for ap in allele_profiles:
        ap.sample_id = sample.id  # type: ignore[assignment]
        ap.locus_set_id = locus_set.id  # type: ignore[assignment]
        ap.locus_detection_protocol_id = locus_detection_protocol.id  # type: ignore[assignment]
        ap.seq_id = uuid.uuid4()  # type: ignore[assignment]

    seq_distance_protocol = get_seq_distance_protocol(locus_set)
    profile_ids = get_allele_profile_ids(allele_profiles)
    distance_matrix = SeqdbTestClient.calculate_distance_matrix_from_allele_profiles(
        allele_profiles
    )
    seq_distances = get_seq_distances(
        allele_profiles, sample, seq_distance_protocol, profile_ids, distance_matrix
    )

    # create a 'dict' repository from the demo models as dict[class/model] = {instance.id: instance}
    db: dict[type, dict[UUID, Any]] = {}
    db[model.LocusSet] = {locus_set.id: locus_set}  # type: ignore[dict-item]
    db[model.LocusDetectionProtocol] = {
        locus_detection_protocol.id: locus_detection_protocol  # type: ignore[dict-item]
    }
    db[model.DataCollection] = {data_collection.id: data_collection}  # type: ignore[dict-item]
    db[model.Sample] = {sample.id: sample}  # type: ignore[dict-item]
    db[model.SeqDistanceProtocol] = {seq_distance_protocol.id: seq_distance_protocol}  # type: ignore[dict-item]
    db[model.AlleleProfile] = {x.id: x for x in allele_profiles}  # type: ignore[misc]
    db[model.SeqDistance] = {x.profile_id: x for x in seq_distances}

    return db


def get_seq_distances(
    allele_profiles: list[model.AlleleProfile],
    sample: model.Sample,
    seq_distance_protocol: model.SeqDistanceProtocol,
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
            sample_id=sample.id,
            seq_id=allele_profiles[i].seq_id,
            seq_distance_protocol_id=seq_distance_protocol.id,  # type: ignore[arg-type]
            profile_id=profile_ids[i],
            distance_format=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
            distances=pd.Series(distances_dict).to_json(),
        )
        seq_distances.append(seq_distance)
    return seq_distances


def get_allele_profile_ids(allele_profiles: list[model.AlleleProfile]) -> list[UUID]:
    profile_ids: list[UUID] = []
    for allele_profile in allele_profiles:
        if allele_profile.id is None:
            allele_profile.id = uuid.uuid4()
        profile_ids.append(allele_profile.id)
    assert len(profile_ids) == len(allele_profiles)
    return profile_ids


def get_seq_distance_protocol(locus_set: model.LocusSet) -> model.SeqDistanceProtocol:
    seq_distance_protocol = model.SeqDistanceProtocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="ALLELE_HAMMING_TEST",
        name="Allele Hamming Test",
        version="1.0",
        is_integer_distance=True,
        seq_distance_protocol_type=enum.SeqDistanceProtocolType.ALLELE_HAMMING,
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


def get_locus_detection_protocol() -> model.LocusDetectionProtocol:
    locus_detection_protocol = model.LocusDetectionProtocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code="LDP_TEST",
        name="Locus Detection Protocol Test",
        version="1.0",
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


def convert_upload_to_profile(
    upload_profile: model.AlleleProfileForUpload,
) -> model.AlleleProfile:
    """Convert `AlleleProfileForUpload` to a persisted-ready `AlleleProfile`.

    - Sorts allele IDs (None -> `NULL_ID`) and encodes them as base64 string.
    - Computes a deterministic hash for the profile's byte representation.
    - Counts non-null loci to populate `n_loci`.
    """
    if not upload_profile.allele_ids:
        raise ValueError("allele_ids must be provided in AlleleProfileForUpload")

    sorted_allele_ids = sorted(upload_profile.allele_ids, key=lambda x: x or NULL_ID)
    allele_bytes_list = [
        (allele_id.bytes if allele_id else NULL_ID.bytes)
        for allele_id in sorted_allele_ids
    ]
    allele_profile_bytes = b"".join(allele_bytes_list)
    allele_profile_str = base64.b64encode(allele_profile_bytes).decode("ascii")

    sha256 = hashlib.sha256()
    sha256.update(allele_profile_bytes)
    allele_profile_hash = UUID(sha256.digest()[:16].hex())

    # n_loci must reflect the number of detected loci, excluding both
    # `None` and sentinel `NULL_ID` values. The model validator counts
    # non-null 16-byte chunks by comparing to `NULL_ID.bytes`.
    n_loci = sum(
        1
        for allele_id in upload_profile.allele_ids
        if (allele_id is not None and allele_id != NULL_ID)
    )

    allele_profile = model.AlleleProfile(  # type: ignore[call-arg]
        sample_id=upload_profile.sample_id,
        seq_id=upload_profile.seq_id,
        locus_set_id=upload_profile.locus_set_id,
        locus_detection_protocol_id=upload_profile.locus_detection_protocol_id,
        n_loci=n_loci,
        allele_profile=allele_profile_str,
        allele_profile_format=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
        allele_profile_hash=allele_profile_hash,
    )

    return allele_profile


def convert_allele_profile_for_upload(
    batch: model.SampleBatchForUpload,
) -> list[model.AlleleProfile]:
    allele_profiles: list[model.AlleleProfile] = []
    for sample in batch.samples:
        for upload_ap in sample.allele_profiles:  # type: ignore[union-attr]
            allele_profiles.append(convert_upload_to_profile(upload_ap))
    return allele_profiles


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
