import json
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.services.seq.retrieve_seq_distances_by_seq_profiles import (
    seq_service_retrieve_seq_distances_by_seq_profiles,
)


class _RepositoryStub:
    def __init__(
        self,
        distances: list[model.SeqDistance],
        profile_ids: list[UUID],
        protocol_id: UUID,
        user_id: UUID | None,
    ) -> None:
        self.distances = distances
        self.profile_ids = frozenset(profile_ids)
        self.protocol_id = protocol_id
        self.user_id = user_id

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
        assert user_id == self.user_id
        assert model_class is model.SeqDistance
        assert operation is CrudOperation.READ_ALL
        distance_filter = kwargs["filter"]
        assert isinstance(distance_filter, CompositeFilter)
        assert distance_filter.operator is LogicalOperator.AND
        profile_filter, protocol_filter = distance_filter.filters
        assert isinstance(profile_filter, UuidSetFilter)
        assert profile_filter.key == "seq_profile_id"
        assert profile_filter.members == self.profile_ids
        assert isinstance(protocol_filter, EqualsUuidFilter)
        assert protocol_filter.key == "protocol_id"
        assert protocol_filter.value == self.protocol_id
        return self.distances


class _ServiceStub:
    def __init__(
        self,
        distances: list[model.SeqDistance],
        profile_ids: list[UUID],
        protocol_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        self.repository = _RepositoryStub(distances, profile_ids, protocol_id, user_id)


def test_retrieve_seq_distances_by_seq_profiles_returns_repository_records() -> None:
    """Return distance records selected by profile IDs and protocol."""
    protocol_id = uuid4()
    profile_ids = [uuid4(), uuid4()]
    distance = model.SeqDistance(
        id=uuid4(),
        sample_id=uuid4(),
        protocol_id=protocol_id,
        seq_profile_id=profile_ids[0],
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps({str(uuid4()): 1.5}),
    )
    service = _ServiceStub([distance], profile_ids, protocol_id)
    cmd = command.RetrieveSeqDistancesBySeqProfilesCommand(
        seq_profile_ids=profile_ids,
        protocol_id=protocol_id,
    )

    result = seq_service_retrieve_seq_distances_by_seq_profiles(service, cmd)  # type: ignore[arg-type]

    assert result == [distance]


def test_retrieve_seq_distances_by_seq_profiles_forwards_user_id() -> None:
    """Forward the authenticated user's ID to the repository."""
    protocol_id = uuid4()
    profile_ids = [uuid4()]
    user_id = uuid4()
    service = _ServiceStub([], profile_ids, protocol_id, user_id)
    cmd = command.RetrieveSeqDistancesBySeqProfilesCommand(
        seq_profile_ids=profile_ids,
        protocol_id=protocol_id,
        user=User(
            id=user_id,
            roles={"user"},
            organization_id=uuid4(),
        ),
    )

    result = seq_service_retrieve_seq_distances_by_seq_profiles(service, cmd)  # type: ignore[arg-type]

    assert result == []


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
