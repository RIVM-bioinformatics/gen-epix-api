from dataclasses import dataclass
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from uuid import UUID


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
