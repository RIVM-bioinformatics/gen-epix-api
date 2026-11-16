from dataclasses import dataclass
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from typing import Any
from uuid import UUID, uuid4

from gen_epix.seqdb.domain import enum, model


@dataclass(frozen=True)
class SeqUploadRefData:
    """Reference records needed for sample uploads."""

    data_collection_id: UUID
    assembly_protocol_id: UUID
    sequencing_protocol_id: UUID


def create_ref_data(env: Env) -> SeqUploadRefData:
    root_user = env.get_root_user()
    env.set_obj(root_user)
    data_collection = env.create_data_collection(root_user, "upload_data_collection")
    assembly = env.create_assembly_protocol(root_user, "upload_assembly")
    sequencing = env.create_sequencing_protocol(root_user, "upload_sequencing")
    assert data_collection.id and assembly.id and sequencing.id
    return SeqUploadRefData(data_collection.id, assembly.id, sequencing.id)


def create_sample_for_upload(
    ref_data: SeqUploadRefData,
    code: str | None = None,
    seq_protocol: dict[str, Any] | None = None,
) -> model.SampleForUpload:
    """Create a sample, optionally with one sequence using the given protocol."""
    sample = model.Sample(
        code=code or uuid4().hex,
        created_in_data_collection_id=ref_data.data_collection_id,
    )
    if seq_protocol is None:
        return model.SampleForUpload(sample=sample)
    return model.SampleForUpload(
        sample=sample,
        seqs=[
            model.SeqForUpload(
                id=uuid4(),
                contigs=[
                    model.Contig(
                        # Keep sequence hashes distinct across test samples.
                        seq="".join("ACGT"[int(x, 16) % 4] for x in uuid4().hex),
                        seq_format=enum.SeqFormat.STR_DNA,
                    )
                ],
                **seq_protocol,
            )
        ],
    )
