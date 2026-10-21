"""Tests for protocol CRUD validation rules."""

from test.util.mock_compat import MagicMock
from uuid import uuid4

import pytest

from gen_epix.seqdb.domain.enum import ProtocolType
from gen_epix.seqdb.domain.model.seq.protocol import Protocol
from gen_epix.seqdb.services.seq.crud_protocol import (
    _validate_protocol_creation,
    _validate_protocol_updates,
)

_COMMIT_HASH = "0123456789abcdef0123456789abcdef01234567"


def _protocol(
    protocol_type: ProtocolType = ProtocolType.ASSEMBLY,
    git_commit_hash: str | None = None,
    protocol_id=None,
) -> Protocol:
    return Protocol(
        id=protocol_id,
        code=f"protocol-{uuid4()}",
        protocol_type=protocol_type,
        git_commit_hash=git_commit_hash,
    )


def _service(existing_protocols: list[Protocol] | None = None) -> MagicMock:
    service = MagicMock()
    service.repository.crud.return_value = existing_protocols or []
    return service


def test_protocol_creation_rejects_duplicate_hash_in_existing_protocols() -> None:
    """Reject commit hashes already used by the same protocol type."""
    service = _service([_protocol(git_commit_hash=_COMMIT_HASH)])

    with pytest.raises(ValueError, match="already exists"):
        _validate_protocol_creation(
            service, None, [_protocol(git_commit_hash=_COMMIT_HASH)]
        )


def test_protocol_creation_allows_same_hash_for_different_types() -> None:
    """Scope commit-hash uniqueness to protocol type."""
    service = _service([_protocol(git_commit_hash=_COMMIT_HASH)])

    _validate_protocol_creation(
        service,
        None,
        [
            _protocol(
                protocol_type=ProtocolType.SEQUENCING,
                git_commit_hash=_COMMIT_HASH,
            )
        ],
    )


def test_protocol_update_rejects_protocol_type_change() -> None:
    """Keep protocol type immutable for existing records."""
    protocol_id = uuid4()
    service = _service([_protocol(protocol_id=protocol_id)])

    with pytest.raises(ValueError, match="immutable field"):
        _validate_protocol_updates(
            service,
            None,
            [_protocol(ProtocolType.SEQUENCING, protocol_id=protocol_id)],
        )


def test_protocol_update_allows_unchanged_protocol_type() -> None:
    """Allow updates that preserve the existing protocol type."""
    protocol_id = uuid4()
    service = _service([_protocol(protocol_id=protocol_id)])

    _validate_protocol_updates(service, None, [_protocol(protocol_id=protocol_id)])
