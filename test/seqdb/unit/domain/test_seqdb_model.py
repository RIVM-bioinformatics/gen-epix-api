"""
Unit tests for gen_epix.seqdb.domain.model.seq.protocol.Protocol.

Tests cover:
- Construction (happy paths for all ProtocolType values)
- _validate_git_commit_hash
- _validate_git_repository_uri
- _validate_props
- _validate_protocol_type_dependencies
- Serializers (_serialize_protocol_type, _serialize_ref_seq_id)

Note: is_integer_distance and max_stored_distance have no default value in the
Protocol model, so they must be passed explicitly even when None (for non-
SEQ_DISTANCE types). The _minimal_protocol_data helper handles this convention.
"""

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.enum import (
    ProtocolType,
    ProtocolTypeSet,
    SeqDistanceType,
    SeqProfileType,
)
from gen_epix.seqdb.domain.model.seq.protocol import Protocol

# ---------------------------------------------------------------------------
# Module-level sample values
# ---------------------------------------------------------------------------

SAMPLE_REF_SEQ_ID: UUID = uuid4()
SAMPLE_LOCUS_SET_ID: UUID = uuid4()
SAMPLE_SEQ_CATEGORY_SET_ID: UUID = uuid4()

VALID_GIT_HASH: str = "a" * 40
VALID_GIT_URI: str = "https://github.com/example/repo"

# Natural mapping from each SEQ_PROFILE ProtocolType to a SeqProfileType value.
_SEQ_PROFILE_TYPE_MAP: dict[ProtocolType, SeqProfileType] = {
    ProtocolType.SEQ_PROFILE: SeqProfileType.ALLELE,
    ProtocolType.SEQ_PROFILE: SeqProfileType.MLVA,
    ProtocolType.SEQ_PROFILE: SeqProfileType.SNP,
    ProtocolType.SEQ_PROFILE: SeqProfileType.LOCUS,
    ProtocolType.SEQ_PROFILE: SeqProfileType.KMER,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_protocol_data(protocol_type: ProtocolType) -> dict[str, Any]:
    """Returns the minimal valid field dict for the given protocol_type.

    For non-SEQ_DISTANCE types, is_integer_distance and max_stored_distance
    are explicitly set to None because they have no model-level default.
    """
    data: dict[str, Any] = {
        "code": f"{protocol_type.value}_001",
        "protocol_type": protocol_type,
        "is_integer_distance": None,
        "max_stored_distance": None,
    }
    if protocol_type in ProtocolTypeSet.HAS_REF_SEQ.value:
        data["ref_seq_id"] = SAMPLE_REF_SEQ_ID
    if protocol_type in ProtocolTypeSet.HAS_SEQ_CATEGORY_SET.value:
        data["seq_category_set_id"] = SAMPLE_SEQ_CATEGORY_SET_ID
    if protocol_type in ProtocolTypeSet.HAS_LOCUS_SET.value:
        data["locus_set_id"] = SAMPLE_LOCUS_SET_ID
    if protocol_type in ProtocolTypeSet.SEQ_PROFILE.value:
        data["seq_profile_type"] = _SEQ_PROFILE_TYPE_MAP[protocol_type]
    if protocol_type in ProtocolTypeSet.IS_SEQ_DISTANCE.value:
        data["is_integer_distance"] = True
        data["max_stored_distance"] = 100.0
        data["seq_distance_type"] = SeqDistanceType.ALLELE_HAMMING
    return data


def _make_protocol(**overrides: Any) -> Protocol:
    """Creates a minimal SEQUENCING Protocol, applying any given field overrides."""
    data = _minimal_protocol_data(ProtocolType.SEQUENCING)
    data.update(overrides)
    return Protocol(**data)


# ---------------------------------------------------------------------------
# Happy paths: all ProtocolType values
# ---------------------------------------------------------------------------


class TestProtocolHappyPaths:
    """Valid construction for every ProtocolType."""

    @pytest.mark.parametrize("protocol_type", list(ProtocolType))
    def test_valid_instantiation_for_all_protocol_types(
        self, protocol_type: ProtocolType
    ) -> None:
        data = _minimal_protocol_data(protocol_type)
        protocol = Protocol(**data)
        assert protocol.protocol_type == protocol_type
        assert protocol.code == data["code"]

    def test_optional_metadata_fields_accepted(self) -> None:
        """Optional metadata fields are accepted when all are provided."""
        protocol = _make_protocol(
            name="My Protocol",
            description="A detailed description.",
            git_repository_uri=VALID_GIT_URI,
            git_commit_hash=VALID_GIT_HASH,
            git_commit_tag="v1.0.0",
            valid_start_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
            valid_end_datetime=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        assert protocol.name == "My Protocol"
        assert protocol.git_commit_hash == VALID_GIT_HASH
        assert protocol.git_commit_tag == "v1.0.0"
        assert protocol.valid_start_datetime == datetime(
            2024, 1, 1, tzinfo=timezone.utc
        )
        assert protocol.valid_end_datetime == datetime(2025, 1, 1, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# _validate_git_commit_hash
# ---------------------------------------------------------------------------


class TestProtocolGitCommitHash:
    """Tests for the git_commit_hash field validator."""

    def test_none_is_accepted(self) -> None:
        protocol = _make_protocol(git_commit_hash=None)
        assert protocol.git_commit_hash is None

    def test_valid_40_char_lowercase_hex(self) -> None:
        protocol = _make_protocol(git_commit_hash=VALID_GIT_HASH)
        assert protocol.git_commit_hash == VALID_GIT_HASH

    def test_valid_40_char_uppercase_hex(self) -> None:
        git_hash = "A" * 40
        protocol = _make_protocol(git_commit_hash=git_hash)
        assert protocol.git_commit_hash == git_hash

    def test_valid_40_char_mixed_hex(self) -> None:
        git_hash = "0123456789abcdefABCDEF0123456789abcdef01"
        protocol = _make_protocol(git_commit_hash=git_hash)
        assert protocol.git_commit_hash == git_hash

    @pytest.mark.parametrize("length", [0, 7, 39])
    def test_hex_wrong_length_raises(self, length: int) -> None:
        # max_length=40 on the field rejects lengths > 40 before the validator;
        # the validator itself rejects lengths != 40.
        with pytest.raises(ValidationError):
            _make_protocol(git_commit_hash="a" * length)

    def test_non_hex_40_char_string_raises(self) -> None:
        with pytest.raises(ValidationError):
            _make_protocol(git_commit_hash="z" * 40)

    def test_hex_string_with_0x_prefix_raises(self) -> None:
        # string.hexdigits does not include 'x', so "0x"-prefixed strings are invalid.
        git_hash = "0x" + "a" * 38
        with pytest.raises(ValidationError):
            _make_protocol(git_commit_hash=git_hash)


# ---------------------------------------------------------------------------
# _validate_git_repository_uri
# ---------------------------------------------------------------------------


class TestProtocolGitRepositoryUri:
    """Tests for the git_repository_uri field validator."""

    def test_none_is_accepted(self) -> None:
        protocol = _make_protocol(git_repository_uri=None)
        assert protocol.git_repository_uri is None

    @pytest.mark.parametrize(
        "uri",
        [
            "https://github.com/example/repo",
            "http://internal.example.com/repo.git",
            "https://gitlab.com/group/subgroup/project",
        ],
    )
    def test_valid_uris_accepted(self, uri: str) -> None:
        protocol = _make_protocol(git_repository_uri=uri)
        assert protocol.git_repository_uri == uri

    @pytest.mark.parametrize(
        "uri",
        [
            "github.com/example/repo",  # no scheme
            "/local/path/to/repo",  # path only, no scheme or netloc
            "://missing-scheme.com/repo",  # empty scheme
        ],
    )
    def test_invalid_uris_raise(self, uri: str) -> None:
        with pytest.raises(ValidationError):
            _make_protocol(git_repository_uri=uri)


# ---------------------------------------------------------------------------
# _validate_props
# ---------------------------------------------------------------------------


class TestProtocolProps:
    """Tests for the props field validator."""

    def test_empty_dict_is_default(self) -> None:
        protocol = _make_protocol()
        assert protocol.props == {}

    def test_dict_with_data_accepted(self) -> None:
        props = {"key": "value", "number": 42}
        protocol = _make_protocol(props=props)
        assert protocol.props == props

    def test_valid_json_string_is_parsed_to_dict(self) -> None:
        props = {"key": "value"}
        protocol = _make_protocol(props=json.dumps(props))
        assert protocol.props == props

    def test_non_dict_non_string_raises(self) -> None:
        with pytest.raises(ValidationError):
            _make_protocol(props=["not", "a", "dict"])

    def test_invalid_json_string_raises(self) -> None:
        with pytest.raises(ValidationError):
            _make_protocol(props="{not valid json")

    def test_dict_at_max_json_length_accepted(self) -> None:
        max_len = Protocol.PROPS_MAX_JSON_LENGTH
        # '{"k": "' = 7 chars, '"}' = 2 chars; fill the remainder with the value
        prefix = '{"k": "'
        suffix = '"}'
        value = "v" * (max_len - len(prefix) - len(suffix))
        props = {"k": value}
        assert len(json.dumps(props)) == max_len
        protocol = _make_protocol(props=props)
        assert protocol.props == props

    def test_dict_exceeding_max_json_length_raises(self) -> None:
        max_len = Protocol.PROPS_MAX_JSON_LENGTH
        # value alone is already longer than max_len, so the full JSON will exceed it
        props = {"key": "x" * max_len}
        with pytest.raises(ValidationError):
            _make_protocol(props=props)

    def test_json_string_exceeding_max_length_raises(self) -> None:
        max_len = Protocol.PROPS_MAX_JSON_LENGTH
        long_json = json.dumps({"key": "x" * max_len})
        assert len(long_json) > max_len
        with pytest.raises(ValidationError):
            _make_protocol(props=long_json)


# ---------------------------------------------------------------------------
# _validate_protocol_type_dependencies
# ---------------------------------------------------------------------------

# Tuples of (field_name, protocol_type that requires it) for "missing" tests.
_REQUIRED_FIELD_CASES: list[tuple[str, ProtocolType]] = [
    ("seq_category_set_id", ProtocolType.SEQ_CLASSIFICATION),
    ("seq_profile_type", ProtocolType.SEQ_PROFILE),
    ("seq_distance_type", ProtocolType.SEQ_DISTANCE),
    ("is_integer_distance", ProtocolType.SEQ_DISTANCE),
    ("max_stored_distance", ProtocolType.SEQ_DISTANCE),
]

# Tuples of (field_name, protocol_type that does NOT require it, non-None value)
# for "extra field" tests.
_EXTRA_FIELD_CASES: list[tuple[str, ProtocolType, Any]] = [
    ("ref_seq_id", ProtocolType.SEQUENCING, SAMPLE_REF_SEQ_ID),
    ("seq_category_set_id", ProtocolType.SEQUENCING, SAMPLE_SEQ_CATEGORY_SET_ID),
    ("locus_set_id", ProtocolType.SEQUENCING, SAMPLE_LOCUS_SET_ID),
    ("seq_profile_type", ProtocolType.SEQUENCING, SeqProfileType.SNP),
    ("seq_distance_type", ProtocolType.SEQUENCING, SeqDistanceType.ALLELE_HAMMING),
    ("is_integer_distance", ProtocolType.SEQUENCING, True),
    ("max_stored_distance", ProtocolType.SEQUENCING, 50.0),
]


class TestProtocolTypeDependencies:
    """Tests for the _validate_protocol_type_dependencies model validator."""

    @pytest.mark.parametrize(
        "field_name, protocol_type",
        _REQUIRED_FIELD_CASES,
        ids=[x[0] for x in _REQUIRED_FIELD_CASES],
    )
    def test_missing_required_field_raises(
        self, field_name: str, protocol_type: ProtocolType
    ) -> None:
        """A field required by the protocol_type must not be None."""
        data = _minimal_protocol_data(protocol_type)
        data[field_name] = None
        with pytest.raises(ValidationError):
            Protocol(**data)

    @pytest.mark.parametrize(
        "field_name, protocol_type, value",
        _EXTRA_FIELD_CASES,
        ids=[x[0] for x in _EXTRA_FIELD_CASES],
    )
    def test_extra_field_set_when_not_required_raises(
        self, field_name: str, protocol_type: ProtocolType, value: Any
    ) -> None:
        """A field not required by the protocol_type must be None."""
        data = _minimal_protocol_data(protocol_type)
        data[field_name] = value
        with pytest.raises(ValidationError):
            Protocol(**data)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


class TestProtocolSerializers:
    """Tests for Protocol field serializers."""

    def test_protocol_type_serialized_as_string(self) -> None:
        protocol = _make_protocol()
        dumped = protocol.model_dump(mode="json")
        assert dumped["protocol_type"] == ProtocolType.SEQUENCING.value
        assert isinstance(dumped["protocol_type"], int)

    def test_ref_seq_id_serialized_as_string(self) -> None:
        data = _minimal_protocol_data(ProtocolType.SEQ_PROFILE)
        data["ref_seq_id"] = SAMPLE_REF_SEQ_ID  # optional for SEQ_PROFILE
        protocol = Protocol(**data)
        dumped = protocol.model_dump(mode="json")
        assert dumped["ref_seq_id"] == str(SAMPLE_REF_SEQ_ID)
        assert isinstance(dumped["ref_seq_id"], str)

    def test_locus_set_id_serialized_as_string(self) -> None:
        data = _minimal_protocol_data(ProtocolType.SEQ_PROFILE)
        data["locus_set_id"] = SAMPLE_LOCUS_SET_ID  # optional for SEQ_PROFILE
        protocol = Protocol(**data)
        dumped = protocol.model_dump(mode="json")
        assert dumped["locus_set_id"] == str(SAMPLE_LOCUS_SET_ID)
        assert isinstance(dumped["locus_set_id"], str)

    def test_none_ref_seq_id_serialized_as_none(self) -> None:
        protocol = _make_protocol()
        dumped = protocol.model_dump(mode="json")
        assert dumped["ref_seq_id"] is None

    def test_none_locus_set_id_serialized_as_none(self) -> None:
        protocol = _make_protocol()
        dumped = protocol.model_dump(mode="json")
        assert dumped["locus_set_id"] is None
