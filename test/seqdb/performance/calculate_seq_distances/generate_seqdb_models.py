import base64
import random
import secrets
import uuid
from datetime import datetime
from typing import Any
from uuid import UUID

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import enum, model


def generate_demo_seqdb_models(
    n_loci: int,
    n_to_create: int,
    snp_seq_length: int = 0,
) -> dict[type, dict[UUID, Any]]:
    """Generate demo seqdb models.

    When snp_seq_length > 0, SNP-specific
    reference data (Taxon, RefSeq, SNP profile
    protocol, SNP distance protocol) is also
    generated for each entry.
    """

    model_types = [
        model.Protocol,
        model.Locus,
        model.LocusSet,
        model.LocusCodeMap,
        model.SeqProfile,
        model.SeqDistance,
        model.Sample,
        model.Taxon,
        model.RefSeq,
    ]

    db: dict[type, dict[UUID, Any]] = {x: {} for x in model_types}

    for i in range(1, n_to_create + 1):

        hex_string = secrets.token_hex(4)

        assembly_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"assembly_protocol_code{hex_string}_{i}",
            name=f"assembly_protocol_name{hex_string}_{i}",
            protocol_type=enum.ProtocolType.ASSEMBLY,
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

        locus_detection_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            code=f"locus_protocol_code{hex_string}_{i}",
            name=f"locus_protocol_name{hex_string}_{i}",
            protocol_type=enum.ProtocolType.SEQ_PROFILE,
            seq_profile_type=enum.SeqProfileType.ALLELE,
            locus_set_id=locus_set.id,
        )

        seq_distance_protocol: model.Protocol = model.Protocol(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            protocol_type=enum.ProtocolType.SEQ_DISTANCE,
            seq_distance_type=enum.SeqDistanceType.ALLELE_HAMMING,
            locus_set_id=locus_set.id,
            valid_start_datetime=datetime(1970, 1, 1),
            valid_end_datetime=datetime(9999, 12, 31),
            is_integer_distance=True,
            max_stored_distance=1000.0,
            code="seq_distance_protocol_code{hex_string}_{i}",
            name="seq_distance_protocol_name{hex_string}_{i}",
        )

        sample = model.Sample(  # type: ignore[call-arg]
            id=uuid.uuid4(),
            created_in_data_collection_id=uuid.uuid4(),
        )

        allele_ids = [uuid.uuid4() for _ in range(1, n_loci + 1)]
        constructed_allele_profile = base64.b64encode(
            b"".join(x.bytes for x in allele_ids)
        ).decode("ascii")

        allele_profile = model.SeqProfile(
            id=uuid.uuid4(),
            seq_profile_type=enum.SeqProfileType.ALLELE,
            protocol_id=locus_detection_protocol.id,
            locus_set_id=locus_set.id,
            n_loci=n_loci,
            format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),
            content=base64.b64encode(
                b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
            ).decode("ascii"),
            sample_id=sample.id,
        )

        seq_distance = model.SeqDistance(  # type: ignore[call-arg]
            protocol_id=seq_distance_protocol.id,  # type: ignore[arg-type]
            seq_profile_id=allele_profile.id,  # type: ignore[arg-type]
            format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            content="{}",
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

        # SNP reference data
        if snp_seq_length > 0:
            snp_objects = _generate_snp_objects(
                hex_string,
                i,
                snp_seq_length,
                sample,
            )
            new_objects.extend(snp_objects)

        for obj in new_objects:
            db[type(obj)][obj.id] = obj

    return db


def _generate_snp_objects(
    hex_string: str,
    index: int,
    seq_length: int,
    sample: model.Sample,
) -> list[Any]:
    """Generate SNP-specific reference objects.

    Creates: Taxon, RefSeq, SNP profile
    protocol, SNP distance protocol, one SNP
    SeqProfile, and one SeqDistance.
    """
    rng = random.Random(42 + index)
    ref_seq_str = "".join(rng.choice("ACGT") for _ in range(seq_length))

    taxon = model.Taxon(
        id=uuid.uuid4(),
        code=f"taxon_{hex_string}_{index}",
        name=f"Taxon {hex_string} {index}",
        rank=enum.TaxonRank.SPECIES,
        ancestor_taxon_ids=[],
    )

    ref_seq = model.RefSeq(
        code=f"ref_seq_{hex_string}_{index}",
        name=f"RefSeq {hex_string} {index}",
        taxon_id=taxon.id,  # type: ignore[arg-type]
        seq=ref_seq_str,
        seq_format=enum.SeqFormat.STR_DNA,
    )

    snp_profile_protocol = model.Protocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code=f"snp_protocol_{hex_string}_{index}",
        name=f"SNP Protocol {hex_string} {index}",
        protocol_type=enum.ProtocolType.SEQ_PROFILE,
        seq_profile_type=enum.SeqProfileType.SNP,
        ref_seq_id=ref_seq.id,
    )

    snp_distance_protocol = model.Protocol(  # type: ignore[call-arg]
        id=uuid.uuid4(),
        code=(f"snp_dist_protocol_{hex_string}" f"_{index}"),
        name=(f"SNP Distance Protocol" f" {hex_string} {index}"),
        protocol_type=enum.ProtocolType.SEQ_DISTANCE,
        seq_distance_type=enum.SeqDistanceType.SNP_HAMMING,
        ref_seq_id=ref_seq.id,
        valid_start_datetime=datetime(1970, 1, 1),
        valid_end_datetime=datetime(9999, 12, 31),
        is_integer_distance=True,
        max_stored_distance=1000.0,
    )

    # One seed SNP profile (the reference
    # itself as aligned seq)
    snp_profile = model.SeqProfile(
        id=uuid.uuid4(),
        seq_profile_type=enum.SeqProfileType.SNP,
        protocol_id=snp_profile_protocol.id,
        format=enum.SeqProfileFormat.REF_ALN_SEQ,
        content_hash=NULL_ID,
        content=ref_seq_str,
        sample_id=sample.id,
    )

    snp_seq_distance = model.SeqDistance(  # type: ignore[call-arg]
        protocol_id=snp_distance_protocol.id,  # type: ignore[arg-type]
        seq_profile_id=snp_profile.id,  # type: ignore[arg-type]
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content="{}",
        sample_id=sample.id,
    )

    return [
        taxon,
        ref_seq,
        snp_profile_protocol,
        snp_distance_protocol,
        snp_profile,
        snp_seq_distance,
    ]
