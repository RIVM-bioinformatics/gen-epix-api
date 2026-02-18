from typing import Any
from uuid import UUID

from gen_epix.seqdb.domain import enum, model


def generate_demo_seqdb_models() -> dict[type, dict[UUID, Any]]:
    locus_detection_protocol: model.LocusDetectionProtocol = model.LocusDetectionProtocol(  # type: ignore[call-arg]
        id=UUID("00000000-0000-0000-0000-000000000001"),
        code="DEMO_PROTOCOL1",
        name="Demo Protocol 1",
    )
    assembly_protocol: model.AssemblyProtocol = model.AssemblyProtocol(  # type: ignore[call-arg]
        id=UUID("00000000-0000-0000-0000-000000000002"),
        code="DEMO_ASSEMBLY_PROTOCOL1",
        name="Demo Assembly Protocol 1",
    )
    
    loci: list[model.Locus] = []
    for i in range(1, 6):
        locus = model.Locus(
            id=UUID(f"00000000-0000-0000-0000-00000000001{i}"),
            code=f"locus{i}",
            locus_type=enum.LocusType.OTHER,
        )
        loci.append(locus)
    
    locus_set: model.LocusSet = model.LocusSet(
        id=UUID("00000000-0000-0000-0000-000000000021"),
        code="locus_set1",
        name="Demo Locus Set 1",
        locus_ids=[locus.id for locus in loci],  # type: ignore[list-item]
    )

    locus_code_map: model.LocusCodeMap = model.LocusCodeMap(
        id=UUID("00000000-0000-0000-0000-000000000031"),
        code="DEMO_LOCUS_CODE_MAP",
        code_map={locus.code: locus.id for locus in loci},  # type: ignore[dict-item]
    )

    db: dict[type, dict[UUID, Any]] = {}
    db[model.LocusDetectionProtocol] = {locus_detection_protocol.id: locus_detection_protocol}  # type: ignore[dict-item]
    db[model.AssemblyProtocol] = {assembly_protocol.id: assembly_protocol}  # type: ignore[dict-item]
    db[model.Locus] = {locus.id: locus for locus in loci}  # type: ignore[dict-item]
    db[model.LocusSet] = {locus_set.id: locus_set}  # type: ignore[dict-item]
    db[model.LocusCodeMap] = {locus_code_map.id: locus_code_map}  # type: ignore[dict-item]

    return db
