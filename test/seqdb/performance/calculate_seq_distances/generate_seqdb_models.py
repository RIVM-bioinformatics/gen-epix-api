import base64
import secrets
import uuid
from typing import Any
from uuid import UUID

from gen_epix.seqdb.domain import enum, model


def generate_demo_seqdb_models(
    n_loci: int, n_to_create: int
) -> dict[type, dict[UUID, Any]]:

    model_types = [
        model.Protocol,
        model.Locus,
        model.LocusSet,
        model.LocusCodeMap,
        model.AlleleProfile,
        model.SeqDistance,
        model.Sample,
    ]

    db: dict[type, dict[UUID, Any]] = {x: {} for x in model_types}

    for i in range(1, n_to_create + 1):

        hex_string = secrets.token_hex(4)

        locus_detection_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"locus_protocol_code{hex_string}_{i}",
            name=f"locus_protocol_name{hex_string}_{i}",
            type=enum.ProtocolType.LOCUS_DETECTION,
        )
        assembly_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"assembly_protocol_code{hex_string}_{i}",
            name=f"assembly_protocol_name{hex_string}_{i}",
            type=enum.ProtocolType.ASSEMBLY,
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

        seq_distance_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            protocol_type=enum.ProtocolType.SEQ_DISTANCE,
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
                protocol_id=locus_detection_protocol.id,
                n_loci=n_loci,
                allele_profile=constructed_allele_profile,
                allele_profile_hash=base64.b64encode(uuid.uuid4().bytes).decode(
                    "ascii"
                ),
                sample_id=sample.id,
            )
        )

        seq_distance = model.SeqDistance(  # type: ignore[call-arg]
            protocol_id=seq_distance_protocol.id,  # type: ignore[arg-type]
            profile_id=allele_profile.id,  # type: ignore[arg-type]
            distance_format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            distances="{}",
            sample_id=allele_profile.sample_id,
        )

        new_objects: list[Any] = [
            locus_detection_protocol,
            assembly_protocol,
            *loci,
            locus_set,
            locus_code_map,
            seq_distance_protocol,
            allele_profile,
            seq_distance,
            sample,
        ]
        for obj in new_objects:
            db[type(obj)][obj.id] = obj

    return db
