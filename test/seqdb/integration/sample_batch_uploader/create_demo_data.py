import base64
import secrets
import uuid
from typing import Any
from uuid import UUID

from gen_epix.seqdb.domain import enum, model


def generate_demo_seqdb_models(
    n_loci: int, n_to_create: int
) -> dict[type, dict[UUID, Any]]:

    db: dict[type, dict[UUID, Any]] = {}
    db[model.LocusDetectionProtocol] = {}
    db[model.AssemblyProtocol] = {}
    db[model.Locus] = {}
    db[model.LocusSet] = {}
    db[model.LocusCodeMap] = {}
    db[model.SeqDistanceProtocol] = {}
    db[model.AlleleProfile] = {}
    db[model.SeqDistance] = {}
    db[model.Sample] = {}

    for i in range(1, n_to_create + 1):

        hex_string = secrets.token_hex(4)

        locus_detection_protocol: model.LocusDetectionProtocol = model.LocusDetectionProtocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"locus_protocol_code{hex_string}_{i}",
            name=f"locus_protocol_name{hex_string}_{i}",
        )
        assembly_protocol: model.AssemblyProtocol = model.AssemblyProtocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"assembly_protocol_code{hex_string}_{i}",
            name=f"assembly_protocol_name{hex_string}_{i}",
        )

        loci: list[model.Locus] = []
        # based on the number of loci that will be created in generate_random_sequences,
        # create the correct number of loci here so that the locus IDs in the generated sequences
        # will match the locus IDs in the demo data
        for j in range(1, n_loci + 1):
            locus = model.Locus(
                id=uuid.uuid4(),
                code=f"locus_code{hex_string}_{i}_{j}",
                name=f"locus_name{hex_string}_{i}_{j}",
                locus_type=enum.LocusType.OTHER,
            )
            loci.append(locus)

        locus_set: model.LocusSet = model.LocusSet(
            id=uuid.uuid4(),
            code="locus_set_code{hex_string}_{i}",
            name="locus_set_name{hex_string}_{i}",
            locus_ids=[locus.id for locus in loci if locus.id is not None],
        )

        locus_code_map: model.LocusCodeMap = model.LocusCodeMap(
            id=uuid.uuid4(),
            code="locus_code_map_code{hex_string}_{i}",
            code_map={locus.code: locus.id for locus in loci if locus.id is not None},
        )

        seq_distance_protocol: model.SeqDistanceProtocol = model.SeqDistanceProtocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            seq_distance_protocol_type=enum.SeqDistanceProtocolType.ALLELE_HAMMING,
            locus_set_id=locus_set.id,
            is_integer_distance=True,
            max_stored_distance=1000.0,
            code="seq_distance_protocol_code{hex_string}_{i}",
            name="seq_distance_protocol_name{hex_string}_{i}",
        )

        sample = model.Sample(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            name="sample_name{hex_string}_{i}",
            created_in_data_collection_id=uuid.uuid4(),
        )

        allele_ids = [uuid.uuid4() for _ in range(1, n_loci + 1)]
        constructed_allele_profile = base64.b64encode(
            b"".join(x.bytes for x in allele_ids)
        ).decode("ascii")

        allele_profile = (
            model.AlleleProfile.model_construct(  # model_construct to bypass validators
                id=uuid.uuid4(),
                locus_set_id=locus_set.id,
                locus_detection_protocol_id=locus_detection_protocol.id,
                n_loci=n_loci,
                allele_profile=constructed_allele_profile,
                allele_profile_hash=base64.b64encode(uuid.uuid4().bytes).decode(
                    "ascii"
                ),
                sample_id=sample.id,
            )
        )

        seq_distance1 = model.SeqDistance(  # type: ignore[call-arg]
            seq_distance_protocol_id=seq_distance_protocol.id,
            profile_id=allele_profile.id,
            distance_format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            distances="{}",
            sample_id=allele_profile.sample_id,
        )

        db[model.LocusDetectionProtocol].update({locus_detection_protocol.id: locus_detection_protocol})  # type: ignore[dict-item]
        db[model.AssemblyProtocol].update({assembly_protocol.id: assembly_protocol})  # type: ignore[dict-item]
        db[model.Locus].update({locus.id: locus for locus in loci if locus.id is not None})
        db[model.LocusSet].update({locus_set.id: locus_set})  # type: ignore[dict-item]
        db[model.LocusCodeMap].update({locus_code_map.id: locus_code_map})  # type: ignore[dict-item]
        db[model.SeqDistanceProtocol].update({seq_distance_protocol.id: seq_distance_protocol})  # type: ignore[dict-item]
        db[model.AlleleProfile].update({allele_profile.id: allele_profile})  # type: ignore[dict-item]
        db[model.SeqDistance].update({seq_distance1.id: seq_distance1})  # type: ignore[dict-item]
        db[model.Sample].update({sample.id: sample})  # type: ignore[dict-item]

    return db
