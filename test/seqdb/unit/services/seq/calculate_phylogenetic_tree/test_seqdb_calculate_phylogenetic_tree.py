import json
from typing import Any
from unittest.mock import Mock
from uuid import UUID, uuid4

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.services.seq.calculate_phylogenetic_tree import (
    seq_service_calculate_phylogenetic_tree,
)


def _mock_uow() -> Mock:
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


def _make_protocol(protocol_id: UUID) -> model.Protocol:
    return model.Protocol(  # type: ignore[call-arg]
        id=protocol_id,
        code="SNP_HAMMING_TEST",
        name="SNP Hamming Test",
        is_integer_distance=True,
        protocol_type=enum.ProtocolType.SEQ_DISTANCE,
        seq_distance_type=enum.SeqDistanceType.SNP_HAMMING,
        ref_seq_id=uuid4(),
        max_stored_distance=100.0,
    )


def _make_seq_distance(
    *,
    protocol_id: UUID,
    profile_id: UUID,
    distances: dict[str, float],
) -> model.SeqDistance:
    return model.SeqDistance(  # type: ignore[call-arg]
        id=uuid4(),
        sample_id=uuid4(),
        protocol_id=protocol_id,
        seq_profile_id=profile_id,
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps(distances),
    )


class _RepositoryStub:
    def __init__(self, protocol: model.Protocol, distances: list[model.SeqDistance]):
        self.protocol = protocol
        self.distances = distances

    def uow(self) -> Mock:
        return _mock_uow()

    def crud(
        self,
        _uow: Any,
        _user_id: UUID | None,
        model_class: type[Any],
        operation: CrudOperation,
        **_kwargs: Any,
    ) -> Any:
        if model_class is model.Protocol and operation == CrudOperation.READ_ONE:
            return self.protocol
        if model_class is model.SeqDistance and operation == CrudOperation.READ_ALL:
            return self.distances
        raise AssertionError(f"Unexpected crud call: {model_class} {operation}")


class _SeqServiceStub:
    def __init__(self, repository: _RepositoryStub):
        self.repository = repository

    def generate_id(self) -> UUID:
        return uuid4()


def test_calculated_tree_returns_only_leaves_with_distances() -> None:
    protocol_id = uuid4()
    included_profile_ids = [uuid4(), uuid4()]
    missing_profile_id = uuid4()
    protocol = _make_protocol(protocol_id)
    distances = [
        _make_seq_distance(
            protocol_id=protocol_id,
            profile_id=included_profile_ids[0],
            distances={str(included_profile_ids[1]): 3.0},
        ),
        _make_seq_distance(
            protocol_id=protocol_id,
            profile_id=included_profile_ids[1],
            distances={str(included_profile_ids[0]): 3.0},
        ),
    ]
    service = _SeqServiceStub(_RepositoryStub(protocol, distances))
    cmd = command.CalculatePhylogeneticTreeCommand(
        protocol_id=protocol_id,
        tree_algorithm=enum.TreeAlgorithm.SLINK,
        seq_profile_ids=[
            included_profile_ids[0],
            missing_profile_id,
            included_profile_ids[1],
        ],
        leaf_names=["included-a", "missing", "included-b"],
    )

    tree = seq_service_calculate_phylogenetic_tree(service, cmd)  # type: ignore[arg-type]

    assert tree.profile_ids == included_profile_ids
    assert tree.leaf_names == ["included-a", "included-b"]
    assert "included-a" in tree.newick_repr
    assert "included-b" in tree.newick_repr
    assert "missing" not in tree.newick_repr
