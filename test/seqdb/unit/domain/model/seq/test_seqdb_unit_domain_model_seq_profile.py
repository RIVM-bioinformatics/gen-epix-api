"""Tests for sequence profile validation, hashing, and parsing."""

import json
from uuid import UUID

import pytest

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import (
    MLVA_NO_LOCUS_REPEAT_NUMBER,
    NEXTCLADE_REQUIRED_SEQ_KEYS,
)
from gen_epix.seqdb.domain.model.seq.profile import (
    SeqProfile,
    SeqProfileIdentifier,
    _get_nextclade_non_acgtn_snps,
    _get_nextclade_substitution_snps,
)


def _profile(
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    content: str,
    content_hash: UUID = NULL_ID,
) -> SeqProfile:
    """Build a profile without running unrelated inherited validators."""
    return SeqProfile.model_construct(
        content=content,
        content_hash=content_hash,
        format=profile_format,
        seq_profile_type=profile_type,
    )


def _validated_profile(
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    content: str,
    content_hash: UUID = NULL_ID,
) -> SeqProfile:
    """Construct a profile through its full Pydantic validation lifecycle."""
    return SeqProfile(
        content=content,
        content_hash=content_hash,
        format=profile_format,
        protocol_id=NULL_ID,
        sample_id=NULL_ID,
        seq_profile_type=profile_type,
    )


def test_nextclade_substitutions_extract_positions_and_normalize_nucleotides() -> None:
    """Extract changed positions and lowercase substituted nucleotides."""
    assert _get_nextclade_substitution_snps({"substitutions": "A12C,G20T"}) == [
        (12, "c"),
        (20, "t"),
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        ("", []),
        ("N:10-12", [(10, "n"), (11, "n"), (12, "n")]),
        ("X:15", [(15, "x")]),
        ("N:10-11,X:15", [(10, "n"), (11, "n"), (15, "x")]),
    ],
    ids=["missing", "empty", "range", "single", "multiple"],
)
def test_nextclade_non_acgtn_positions_expand_inclusive_ranges(
    value: str | None, expected: list[tuple[int, str]]
) -> None:
    """Expand inclusive non-ACGTN ranges and accept singleton positions."""
    assert _get_nextclade_non_acgtn_snps({"non_acgtns": value}) == expected


def test_nextclade_substitution_helper_ignores_non_string_and_empty_tokens() -> None:
    """Ignore absent or empty substitution fields and empty comma tokens."""
    assert _get_nextclade_substitution_snps({"substitutions": None}) == []
    assert _get_nextclade_substitution_snps({"substitutions": "A1C,,G3T"}) == [
        (1, "c"),
        (3, "t"),
    ]


def test_profile_validators_derive_hash_and_serialize_enum_values() -> None:
    """Validate an allele profile, derive its content hash, and serialize enums."""
    allele_ids = [UUID("00000000-0000-0000-0000-000000000001"), None]
    content = SeqProfile.get_ordered_allele_ids_representation(allele_ids)
    profile = _validated_profile(
        enum.SeqProfileType.ALLELE,
        enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        content,
    )

    assert profile.content_hash == SeqProfile.get_allele_profile_hash(allele_ids)
    assert profile.model_dump()["seq_profile_type"] == enum.SeqProfileType.ALLELE.value
    assert (
        profile.model_dump()["format"] == enum.SeqProfileFormat.ORDERED_ALLELE_IDS.value
    )


@pytest.mark.parametrize(
    ("profile_type", "profile_format", "content"),
    [
        (
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            "[2, null, -1]",
        ),
        (
            enum.SeqProfileType.KMER,
            enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            '{"ACG": 0.5, "CGT": 1.0}',
        ),
        (
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            json.dumps(
                {
                    **dict.fromkeys(NEXTCLADE_REQUIRED_SEQ_KEYS, ""),
                    "alignment_start": 1,
                    "alignment_end": 20,
                    "substitutions": "A4C",
                }
            ),
        ),
    ],
    ids=["mlva", "kmer", "snp"],
)
def test_profile_content_validators_derive_hashes(
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    content: str,
) -> None:
    """Derive and store hashes for supported MLVA, k-mer, and SNP formats."""
    profile = _validated_profile(profile_type, profile_format, content)

    assert profile.content_hash != NULL_ID


def test_profile_validation_rejects_missing_nextclade_fields_and_accepts_extras() -> (
    None
):
    """Require every declared NextClade field while allowing additional metadata."""
    payload = dict.fromkeys(NEXTCLADE_REQUIRED_SEQ_KEYS, "")
    payload.update(alignment_start=1, alignment_end=10, treeName="metadata")
    content = json.dumps(payload)
    profile = _validated_profile(
        enum.SeqProfileType.SNP, enum.SeqProfileFormat.NEXTCLADE, content
    )
    assert profile.get_snps() == []

    del payload["missings"]
    with pytest.raises(ValueError, match="Missing required NextClade fields"):
        _validated_profile(
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            json.dumps(payload),
        )


def test_profile_validation_rejects_mismatched_hash_and_type_format() -> None:
    """Reject supplied hash mismatches and formats incompatible with profile type."""
    content = SeqProfile.get_ordered_allele_ids_representation([])
    with pytest.raises(ValueError, match="content hash does not match"):
        _validated_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content,
            UUID("00000000-0000-0000-0000-000000000001"),
        )

    with pytest.raises(ValueError, match="Invalid format"):
        _validated_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.NEXTCLADE,
            "{}",
        )


def test_allele_validation_rejects_partial_uuid_bytes() -> None:
    """Reject decoded allele data that cannot be divided into UUID-sized IDs."""
    with pytest.raises(ValueError, match="multiple of 16"):
        _validated_profile(
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            "YQ==",
        )


def test_profile_content_validation_rejects_locus_hashing() -> None:
    """Report that locus-profile content hashing is not implemented."""
    with pytest.raises(NotImplementedError, match="Unable to validate locus profile"):
        _validated_profile(
            enum.SeqProfileType.LOCUS,
            enum.SeqProfileFormat.LOCUS_PROFILE_FORMAT1,
            "{}",
        )


@pytest.mark.parametrize(
    ("profile_type", "profile_format", "method", "message"),
    [
        (
            enum.SeqProfileType.ALLELE,
            enum.SeqProfileFormat.NEXTCLADE,
            SeqProfile._validate_allele_profile,
            "Unable to compute content hash",
        ),
        (
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.NEXTCLADE,
            SeqProfile._validate_mlva_profile,
            "Unable to compute content hash",
        ),
        (
            enum.SeqProfileType.KMER,
            enum.SeqProfileFormat.NEXTCLADE,
            SeqProfile._validate_kmer_profile,
            "Unable to compute content hash",
        ),
        (
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            SeqProfile._validate_snp_profile,
            "Unable to compute content hash",
        ),
    ],
    ids=["allele", "mlva", "kmer", "snp"],
)
def test_profile_hash_validators_reject_unsupported_formats(
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    method,
    message: str,
) -> None:
    """Raise a clear not-implemented error for unsupported hash formats."""
    with pytest.raises(NotImplementedError, match=message):
        method(_profile(profile_type, profile_format, ""))


def test_profile_content_validator_skips_empty_upload_representations() -> None:
    """Defer content validation when an upload-only representation is supplied."""
    profile = SeqProfile.model_construct(
        content="",
        content_hash=NULL_ID,
        format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        seq_profile_type=enum.SeqProfileType.ALLELE,
        allele_ids=[],
    )

    assert profile._validate_content() is profile


def test_allele_accessors_preserve_order_and_map_null_sentinels() -> None:
    """Expose ordered allele IDs as bytes, UUIDs, an array, and a count."""
    first_id = UUID("00000000-0000-0000-0000-000000000001")
    third_id = UUID("00000000-0000-0000-0000-000000000003")
    profile = _profile(
        enum.SeqProfileType.ALLELE,
        enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        SeqProfile.get_ordered_allele_ids_representation([first_id, None, third_id]),
    )

    assert profile.get_allele_id_bytes() == [first_id.bytes, None, third_id.bytes]
    assert profile.get_allele_ids() == [first_id, None, third_id]
    assert profile.get_allele_array().tolist() == [first_id.bytes, b"", third_id.bytes]
    assert profile.get_n_loci() == 2


@pytest.mark.parametrize(
    ("method_name", "profile_type", "profile_format", "message"),
    [
        (
            "get_allele_id_bytes",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            "Allele IDs can only be retrieved",
        ),
        (
            "get_allele_ids",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            "Allele IDs can only be retrieved",
        ),
        (
            "get_allele_array",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            "Allele array can only be computed",
        ),
        (
            "get_n_loci",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.NEXTCLADE,
            "Number of loci can only be retrieved",
        ),
    ],
    ids=["allele-bytes", "allele-ids", "allele-array", "locus-count"],
)
def test_allele_accessors_reject_non_allele_profiles(
    method_name: str,
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    message: str,
) -> None:
    """Reject allele-only accessors when called on an SNP profile."""
    profile = _profile(profile_type, profile_format, "{}")
    with pytest.raises(ValueError, match=message):
        getattr(profile, method_name)()


@pytest.mark.parametrize(
    ("method_name", "message"),
    [
        ("get_allele_id_bytes", "Unable to parse allele IDs"),
        ("get_allele_ids", "Unable to parse allele IDs"),
        ("get_allele_array", "Unable to compute allele array"),
        ("get_n_loci", "Unable to parse number of loci"),
    ],
    ids=["allele-bytes", "allele-ids", "allele-array", "locus-count"],
)
def test_allele_accessors_reject_unsupported_formats(
    method_name: str, message: str
) -> None:
    """Reject allele accessors when the profile uses a non-allele format."""
    profile = _profile(
        enum.SeqProfileType.ALLELE,
        enum.SeqProfileFormat.NEXTCLADE,
        "{}",
    )
    with pytest.raises(NotImplementedError, match=message):
        getattr(profile, method_name)()


def test_repeat_and_kmer_accessors_parse_json_content() -> None:
    """Return the JSON array and object represented by MLVA and k-mer profiles."""
    repeat_profile = _profile(
        enum.SeqProfileType.MLVA,
        enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
        "[1, -1, 3]",
    )
    kmer_content = '{"AAA": 0.25, "CCC": 0.75}'
    kmer_profile = _profile(
        enum.SeqProfileType.KMER,
        enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
        kmer_content,
    )

    assert repeat_profile.get_repeat_numbers() == [1, MLVA_NO_LOCUS_REPEAT_NUMBER, 3]
    assert kmer_profile.get_kmer_frequency_map() == {"AAA": 0.25, "CCC": 0.75}


@pytest.mark.parametrize(
    ("method_name", "profile_type", "profile_format", "message"),
    [
        (
            "get_repeat_numbers",
            enum.SeqProfileType.MLVA,
            enum.SeqProfileFormat.NEXTCLADE,
            "Unable to parse repeat numbers",
        ),
        (
            "get_kmer_frequency_map",
            enum.SeqProfileType.KMER,
            enum.SeqProfileFormat.NEXTCLADE,
            "Unable to parse k-mer frequency map",
        ),
        (
            "get_snps",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            "Unable to parse SNPs",
        ),
        (
            "get_missing_seq_ranges",
            enum.SeqProfileType.SNP,
            enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            "Unable to parse missing sequence ranges",
        ),
    ],
    ids=["repeat", "kmer", "snps", "missing-ranges"],
)
def test_profile_accessors_reject_unsupported_formats(
    method_name: str,
    profile_type: enum.SeqProfileType,
    profile_format: enum.SeqProfileFormat,
    message: str,
) -> None:
    """Raise the documented not-implemented errors for unsupported accessors."""
    profile = _profile(profile_type, profile_format, "{}")
    with pytest.raises(NotImplementedError, match=message):
        (
            getattr(profile, method_name)(20)
            if method_name == "get_missing_seq_ranges"
            else getattr(profile, method_name)()
        )


def test_snp_profile_accessors_parse_and_sort_content() -> None:
    """Return the original aligned content, sorted SNPs, and merged missing ranges."""
    payload = {
        **dict.fromkeys(NEXTCLADE_REQUIRED_SEQ_KEYS, ""),
        "alignment_start": 3,
        "alignment_end": 18,
        "substitutions": "A12C,G5T",
        "non_acgtns": "R:8-9,N:15",
        "missings": "10,13-14",
    }
    content = json.dumps(payload)
    profile = _profile(
        enum.SeqProfileType.SNP,
        enum.SeqProfileFormat.NEXTCLADE,
        content,
    )

    assert profile.get_aligned_nucleotide_seq(ref_seq_str="unused") == content
    assert profile.get_snps() == [
        (5, "t"),
        (8, "r"),
        (9, "r"),
        (12, "c"),
        (15, "n"),
    ]
    assert profile.get_missing_seq_ranges(20) == [
        (1, 2),
        (10, 10),
        (13, 14),
        (19, 20),
    ]


def test_snp_profile_missing_ranges_handle_aligned_empty_and_single_positions() -> None:
    """Handle exact alignment boundaries and singleton internal missing positions."""
    payload = {
        **dict.fromkeys(NEXTCLADE_REQUIRED_SEQ_KEYS, ""),
        "alignment_start": 1,
        "alignment_end": 10,
        "missings": "7",
    }
    profile = _profile(
        enum.SeqProfileType.SNP,
        enum.SeqProfileFormat.NEXTCLADE,
        json.dumps(payload),
    )

    assert profile.get_missing_seq_ranges(10) == [(7, 7)]


def test_profile_type_validator_accepts_enum_name_and_integer() -> None:
    """Normalize supported string and integer profile-type representations."""
    for value in ("ALLELE", enum.SeqProfileType.ALLELE.value):
        profile = _validated_profile(
            value,
            enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            SeqProfile.get_ordered_allele_ids_representation([]),
        )
        assert profile.seq_profile_type == enum.SeqProfileType.ALLELE


def test_profile_hash_helpers_are_order_stable_and_handle_empty_values() -> None:
    """Keep hashes deterministic for sorted k-mers, ordered SNPs, and empty data."""
    first_map = {"CCC": 0.75, "AAA": 0.25}
    second_map = {"AAA": 0.25, "CCC": 0.75}

    assert SeqProfile.get_kmer_profile_hash(
        first_map
    ) == SeqProfile.get_kmer_profile_hash(second_map)
    assert SeqProfile.get_snp_profile_hash([(3, "c"), (1, "a")]) == (
        SeqProfile.get_snp_profile_hash([(1, "a"), (3, "c")])
    )
    assert SeqProfile.get_allele_profile_hash([]) != NULL_ID
    assert SeqProfile.get_mlva_profile_hash([]) != NULL_ID
    assert SeqProfile.get_kmer_profile_hash({}) != NULL_ID
    assert SeqProfile.get_snp_profile_hash([]) != NULL_ID


def test_ordered_profile_representation_helpers_handle_empty_and_null_values() -> None:
    """Encode empty profiles and preserve missing-value sentinels."""
    assert SeqProfile.get_ordered_allele_ids_representation([]) == ""
    assert SeqProfile.get_ordered_repeat_numbers_representation([]) == "[]"
    assert json.loads(
        SeqProfile.get_ordered_repeat_numbers_representation([None, 4])
    ) == [
        MLVA_NO_LOCUS_REPEAT_NUMBER,
        4,
    ]


def test_get_aligned_sequence_rejects_non_snp_profile() -> None:
    """Restrict aligned nucleotide sequence access to SNP profiles."""
    profile = _profile(
        enum.SeqProfileType.ALLELE,
        enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        "",
    )
    with pytest.raises(ValueError, match="only be retrieved for SNP profiles"):
        profile.get_aligned_nucleotide_seq()


def test_profile_identifier_accepts_optional_relationship() -> None:
    """Allow a profile identifier without an eagerly loaded profile relation."""
    assert SeqProfileIdentifier.model_fields["seq_profile"].default is None
