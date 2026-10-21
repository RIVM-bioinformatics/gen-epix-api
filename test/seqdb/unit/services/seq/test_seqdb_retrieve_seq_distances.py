import json
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.services.seq.retrieve_seq_distances_by_seq_profiles import (
    seq_service_retrieve_seq_distances_by_seq_profiles,
)


class _RepositoryStub:
    def __init__(self, distances: list[model.SeqDistance]) -> None:
        self.distances = distances

    def uow(self) -> "_RepositoryStub":
        return self

    def __enter__(self) -> "_RepositoryStub":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def crud(
        self,
        _uow: object,
        user_id: object,
        model_class: type[object],
        operation: CrudOperation,
        **kwargs: object,
    ) -> list[model.SeqDistance]:
        assert user_id is None
        assert model_class is model.SeqDistance
        assert operation is CrudOperation.READ_ALL
        assert kwargs["filter"].filters[0].members  # type: ignore[attr-defined]
        assert kwargs["filter"].filters[1].value  # type: ignore[attr-defined]
        return self.distances


class _ServiceStub:
    def __init__(self, distances: list[model.SeqDistance]) -> None:
        self.repository = _RepositoryStub(distances)


def test_retrieve_seq_distances_by_seq_profiles_returns_repository_records() -> None:
    """Return distance records selected by profile IDs and protocol."""
    protocol_id = uuid4()
    profile_id = uuid4()
    distance = model.SeqDistance(
        id=uuid4(),
        sample_id=uuid4(),
        protocol_id=protocol_id,
        seq_profile_id=profile_id,
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps({str(uuid4()): 1.5}),
    )
    service = _ServiceStub([distance])
    cmd = command.RetrieveSeqDistancesBySeqProfilesCommand(
        seq_profile_ids=[profile_id],
        protocol_id=protocol_id,
    )

    result = seq_service_retrieve_seq_distances_by_seq_profiles(service, cmd)  # type: ignore[arg-type]

    assert result == [distance]


@pytest.mark.parametrize(
    "seq_profile_ids",
    [[], [uuid4(), uuid4()]],
)
def test_retrieve_seq_distances_by_seq_profiles_rejects_invalid_profile_ids(
    seq_profile_ids: list[UUID],
) -> None:
    """Reject empty and duplicate profile selections before dispatch."""
    if len(seq_profile_ids) == 2:
        seq_profile_ids[1] = seq_profile_ids[0]
    with pytest.raises(ValueError):
        command.RetrieveSeqDistancesBySeqProfilesCommand(
            seq_profile_ids=seq_profile_ids,
            protocol_id=uuid4(),
        )
