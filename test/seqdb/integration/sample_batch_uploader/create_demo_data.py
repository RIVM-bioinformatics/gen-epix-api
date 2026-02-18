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
    locus1: model.Locus = model.Locus(
        id=UUID("00000000-0000-0000-0000-000000000011"),
        code="locus1",
        locus_type=enum.LocusType.OTHER,
    )
    locus2: model.Locus = model.Locus(
        id=UUID("00000000-0000-0000-0000-000000000012"),
        code="locus2",
        locus_type=enum.LocusType.OTHER,
    )
    locus_set: model.LocusSet = model.LocusSet(
        id=UUID("00000000-0000-0000-0000-000000000021"),
        code="locus_set1",
        name="Demo Locus Set 1",
        locus_ids=[locus1.id, locus2.id],  # type: ignore[list-item]
    )

    db: dict[type, dict[UUID, Any]] = {}
    db[model.LocusDetectionProtocol] = {locus_detection_protocol.id: locus_detection_protocol}  # type: ignore[dict-item]
    db[model.AssemblyProtocol] = {assembly_protocol.id: assembly_protocol}  # type: ignore[dict-item]
    db[model.Locus] = {
        locus1.id: locus1,  # type: ignore[dict-item]
        locus2.id: locus2,  # type: ignore[dict-item]
    }
    db[model.LocusSet] = {locus_set.id: locus_set}  # type: ignore[dict-item]

    return db
