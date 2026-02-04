import base64
import hashlib
from pathlib import Path
import uuid
from test.seqdb.seqdb_test_client import SeqdbTestClient
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.seqdb.seqdb_test_client import SeqGenerationSettings
from typing import Optional
from uuid import UUID

import pandas as pd

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import command, enum, model


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


def generate_allele_profiles(
    n_seqs: int = 50,
    *,
    settings: Optional[SeqGenerationSettings] = None,
) -> list[model.AlleleProfile]:
    """Generate a list of `AlleleProfile` objects from random sequences.

    Parameters
    - n_seqs: Number of sequences (samples) to generate.
    - settings: Optional `SeqGenerationSettings`; if omitted, uses a default
      configuration suitable for tests.
    """
    if settings is None:
        settings = SeqGenerationSettings(
            n_loci=100,
            locus_length=50,
            p_locus_deletion=0,
            p_nucleotide_substitution=0.0002,
            p_nucleotide_deletion=0.0005,
            seed=1001,
        )

    batch = SeqdbTestClient.generate_random_sequences(n_seqs=n_seqs, settings=settings)

    allele_profiles: list[model.AlleleProfile] = []
    for sample in batch.samples:
        for upload_ap in sample.allele_profiles:
            allele_profiles.append(convert_upload_to_profile(upload_ap))

    return allele_profiles


def generate_demo_data(
    env: Env,
    allele_profiles: list[model.AlleleProfile],
    *,
    sample_id: Optional[UUID] = None,
    locus_set_id: Optional[UUID] = None,
    locus_detection_protocol_id: Optional[UUID] = None,
    seq_distance_protocol_id: Optional[UUID] = None,
) -> tuple[list[UUID], UUID]:
    """Create and persist the full set of demo entities for distance testing.

    This function orchestrates creation (or reuse) of:
    - `LocusSet`
    - `LocusDetectionProtocol`
    - `Sample`
    - `SeqDistanceProtocol`
    - `AlleleProfile` records and corresponding `SeqDistance` entries

    Returns a tuple of (list of `AlleleProfile` IDs, `SeqDistanceProtocol` ID).
    """
    root_user = env.get_root_user()

    assert len(allele_profiles) > 1
    n_loci = allele_profiles[0].n_loci

    # 1) LocusSet
    if locus_set_id is None:
        created_locus_set = env.app.handle(
            command.LocusSetCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.LocusSet(  # type: ignore[call-arg]
                    code="LS_TEST",
                    name="Locus Set Test",
                    n_loci=n_loci,
                    locus_ids=[uuid.uuid4() for _ in range(n_loci)],
                ),
            )
        )
        assert isinstance(created_locus_set, model.LocusSet)
        locus_set_id = created_locus_set.id
        assert locus_set_id is not None

    # 2) LocusDetectionProtocol
    if locus_detection_protocol_id is None:
        created_ldp = env.app.handle(
            command.LocusDetectionProtocolCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.LocusDetectionProtocol(  # type: ignore[call-arg]
                    code="LDP_TEST",
                    name="Locus Detection Protocol Test",
                    version="1.0",
                ),
            )
        )
        assert isinstance(created_ldp, model.LocusDetectionProtocol)
        locus_detection_protocol_id = created_ldp.id
        assert locus_detection_protocol_id is not None

    # 3) Sample linked to an existing DataCollection
    if sample_id is None:
        data_collections = env.app.handle(
            command.DataCollectionCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        assert isinstance(data_collections, list) and len(data_collections) > 0
        dc_id = data_collections[0].id  # type: ignore[attr-defined]
        assert dc_id is not None
        created_sample = env.app.handle(
            command.SampleCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Sample(  # type: ignore[call-arg]
                    code="SAMPLE_TEST",
                    created_in_data_collection_id=dc_id,
                ),
            )
        )
        assert isinstance(created_sample, model.Sample)
        sample_id = created_sample.id
        assert sample_id is not None

    # Assign linkage IDs to allele profiles
    for ap in allele_profiles:
        ap.sample_id = sample_id  # type: ignore[assignment]
        ap.locus_set_id = locus_set_id  # type: ignore[assignment]
        ap.locus_detection_protocol_id = locus_detection_protocol_id  # type: ignore[assignment]
        ap.seq_id = None  # avoid invalid Seq linkage for this happy-flow

    # 4) SeqDistanceProtocol
    if seq_distance_protocol_id is None:
        created_protocol = env.app.handle(
            command.SeqDistanceProtocolCrudCommand(
                user=root_user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.SeqDistanceProtocol(  # type: ignore[call-arg]
                    code="ALLELE_HAMMING_TEST",
                    name="Allele Hamming Test",
                    version="1.0",
                    is_integer_distance=True,
                    seq_distance_protocol_type=enum.SeqDistanceProtocolType.ALLELE_HAMMING,
                    locus_set_id=locus_set_id,
                    max_stored_distance=1e6,
                ),
            )
        )
        assert isinstance(created_protocol, model.SeqDistanceProtocol)
        seq_distance_protocol_id = created_protocol.id
        assert seq_distance_protocol_id is not None

    # 5) Persist allele profiles
    created_profiles = env.app.handle(
        command.AlleleProfileCrudCommand(
            user=root_user,
            operation=CrudOperation.CREATE_SOME,
            objs=allele_profiles,
        )
    )
    assert isinstance(created_profiles, list)
    profile_ids: list[UUID] = [
        p.id for p in created_profiles if p.id is not None  # type: ignore[attr-defined]
    ]
    assert len(profile_ids) == len(allele_profiles)

    # 6) Compute and persist distances
    dist_matrix = SeqdbTestClient.calculate_distance_matrix_from_allele_profile(
        created_profiles  # type: ignore[arg-type]
    )
    assert dist_matrix.matrix.shape[0] == len(profile_ids)

    seq_distances: list[model.SeqDistance] = []
    n = len(profile_ids)
    for i in range(n):
        distances_dict: dict[str, float] = {}
        for j in range(n):
            pid_j = profile_ids[j]
            distances_dict[str(pid_j)] = float(dist_matrix.matrix[i][j])
        seq_distance = model.SeqDistance(  # type: ignore[call-arg]
            sample_id=sample_id,
            seq_id=created_profiles[i].seq_id,  # type: ignore[attr-defined]
            seq_distance_protocol_id=seq_distance_protocol_id,
            profile_id=profile_ids[i],
            distance_format=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
            distances=pd.Series(distances_dict).to_json(),
        )
        seq_distances.append(seq_distance)

    persisted = env.app.handle(
        command.SeqDistanceCrudCommand(
            user=root_user,
            operation=CrudOperation.CREATE_SOME,
            objs=seq_distances,
        )
    )
    assert isinstance(persisted, list)

    return profile_ids, seq_distance_protocol_id


def write_seq_distance_demo_data_to_excel(env: Env) -> None:
    root_user = env.get_root_user()
    excel_file = Path(__file__).parent / "seq_distance_demo_data.xlsx"

    ordered_model_to_sheet_map: dict[type[model.Model], str] = {
        model.Organization: "Organization",
        model.DataCollection: "DataCollection",
        model.User: "User",
        model.LocusSet: "LocusSet",
        model.LocusDetectionProtocol: "LocusDetectionProtocol",
        model.Sample: "Sample",
        model.SeqDistanceProtocol: "SeqDistanceProtocol",
        model.AlleleProfile: "AlleleProfile",
        model.SeqDistance: "SeqDistance",
    }

    with pd.ExcelWriter(excel_file) as writer:
        for model_class, sheet_name in ordered_model_to_sheet_map.items():
            cmd_cls = env.app.domain.get_crud_command_for_model(model_class)
            objs = env.app.handle(
                cmd_cls(
                    user=root_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            records = [
                (o.model_dump() if hasattr(o, "model_dump") else o.dict()) for o in objs
            ]
            df = pd.DataFrame.from_records(records)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    assert excel_file.exists()
