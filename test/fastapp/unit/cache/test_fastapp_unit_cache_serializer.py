"""Tests for cache payload serializers."""

import pytest

from gen_epix.fastapp.cache.exc import CantDeserializeError, SerializationError
from gen_epix.fastapp.cache.serializer import (
    CompressingSerializer,
    DeepCopySerializer,
    IdentitySerializer,
    JsonSerializer,
    PickleSerializer,
    SigningSerializer,
)


def test_the_identity_serializer_shares_references() -> None:
    """Identity serialization preserves the live object reference."""
    serializer = IdentitySerializer()
    value = {"items": [1]}

    assert serializer.loads(serializer.dumps(value)) is value


def test_the_copying_serializer_isolates_both_directions() -> None:
    """Mutating the input after storage cannot mutate the stored copy."""
    serializer = DeepCopySerializer()
    value = {"items": [1]}

    stored = serializer.dumps(value)
    value["items"].append(2)

    assert serializer.loads(stored) == {"items": [1]}


def test_json_and_pickle_round_trip_their_payloads() -> None:
    """Byte serializers recover the payload they encoded."""
    for serializer, value in (
        (JsonSerializer(), {"a": [1, 2]}),
        (PickleSerializer(), {"a": (1, 2)}),
    ):
        assert serializer.loads(serializer.dumps(value)) == value


def test_a_payload_that_cannot_be_encoded_is_reported() -> None:
    """An unsupported JSON value is reported as a serialization failure."""
    with pytest.raises(SerializationError):
        JsonSerializer().dumps(object())


def test_corrupt_bytes_are_reported_as_unreadable() -> None:
    """Corrupt serialized data can be treated as a cache miss."""
    with pytest.raises(CantDeserializeError):
        JsonSerializer().loads(b"not json")


def test_compression_is_applied_only_above_the_threshold() -> None:
    """Small values avoid compression while large values round-trip."""
    serializer = CompressingSerializer(JsonSerializer(), threshold=32)

    small = serializer.dumps("x")
    large = serializer.dumps("y" * 500)

    assert small[:1] == b"\x00"
    assert large[:1] == b"\x01"
    assert serializer.loads(large) == "y" * 500


def test_a_tampered_entry_is_rejected() -> None:
    """A signed payload rejects content changed after signing."""
    serializer = SigningSerializer(JsonSerializer(), secret=b"secret")
    stored = bytearray(serializer.dumps({"role": "user"}))
    stored[-2] ^= 0xFF

    with pytest.raises(CantDeserializeError):
        serializer.loads(bytes(stored))


def test_an_entry_signed_with_another_secret_is_rejected() -> None:
    """Rotating the signing secret makes old entries unreadable."""
    stored = SigningSerializer(JsonSerializer(), secret=b"old").dumps("value")

    with pytest.raises(CantDeserializeError):
        SigningSerializer(JsonSerializer(), secret=b"new").loads(stored)


def test_an_empty_signing_secret_is_refused() -> None:
    """Signing without key material provides no integrity."""
    with pytest.raises(SerializationError):
        SigningSerializer(JsonSerializer(), secret=b"")


def test_a_byte_wrapper_refuses_a_non_byte_inner_serializer() -> None:
    """Compression requires an inner serializer that produces bytes."""
    with pytest.raises(SerializationError):
        CompressingSerializer(IdentitySerializer()).dumps("value")
