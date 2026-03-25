"""
Unit tests for gen_epix.omopdb.domain.model.omop.base module.

Tests cover:
- validate_int_for_uuid_field
- validate_str_for_uuid_field
- validate_str_primary_key_args
- validate_int_primary_key_args
- DataLineageMixin
"""

from uuid import UUID, uuid4

import pytest

from gen_epix.omopdb.domain.model.omop.base import (
    DataLineageMixin,
    validate_int_for_uuid_field,
    validate_int_primary_key_args,
    validate_str_for_uuid_field,
    validate_str_primary_key_args,
)
from gen_epix.util import int_to_uuid, str_to_uuid

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_INT = 42
SAMPLE_STR = "example_key"
SAMPLE_UUID = uuid4()
SAMPLE_UUID_HEX = SAMPLE_UUID.hex  # 32-char string
SAMPLE_UUID_STR = str(SAMPLE_UUID)  # 36-char string with dashes


def _uuid_field_name() -> str:
    return "id"


def _int_field_name() -> str:
    return "concept_id"


def _str_field_name() -> str:
    return "domain_id"


# ---------------------------------------------------------------------------
# Tests for validate_int_for_uuid_field
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestValidateIntForUuidField:
    """Tests for the validate_int_for_uuid_field function."""

    def test_uuid_input_returned_as_is(self) -> None:
        """A UUID input should be returned unchanged."""
        result = validate_int_for_uuid_field(SAMPLE_UUID)
        assert result is SAMPLE_UUID

    @pytest.mark.parametrize("value", [0, 1, 42, 999_999])
    def test_int_input_converted_via_int_to_uuid(self, value: int) -> None:
        """An integer input should be converted to UUID via int_to_uuid."""
        result = validate_int_for_uuid_field(value)
        assert result == int_to_uuid(value)
        assert isinstance(result, UUID)

    def test_str_length_36_parsed_as_uuid(self) -> None:
        """A 36-char string (UUID with dashes) should be parsed as UUID."""
        result = validate_int_for_uuid_field(SAMPLE_UUID_STR)
        assert result == SAMPLE_UUID
        assert isinstance(result, UUID)

    def test_str_length_32_parsed_as_uuid(self) -> None:
        """A 32-char hex string (UUID without dashes) should be parsed as UUID."""
        result = validate_int_for_uuid_field(SAMPLE_UUID_HEX)
        assert result == SAMPLE_UUID
        assert isinstance(result, UUID)

    @pytest.mark.parametrize("value", ["0", "1", "42", "999999"])
    def test_str_numeric_converted_via_int_to_uuid(self, value: str) -> None:
        """A numeric string (not length 32/36) should be parsed as int then
        converted via int_to_uuid."""
        result = validate_int_for_uuid_field(value)
        assert result == int_to_uuid(int(value))
        assert isinstance(result, UUID)

    def test_str_non_numeric_raises_value_error(self) -> None:
        """A non-numeric string that is not a UUID should raise ValueError."""
        with pytest.raises(ValueError):
            validate_int_for_uuid_field("not_a_number")

    def test_none_returns_none(self) -> None:
        """None input should return None."""
        assert validate_int_for_uuid_field(None) is None

    @pytest.mark.parametrize("value", [3.14, [], {}, object()])
    def test_unsupported_type_raises_value_error(self, value: object) -> None:
        """Types other than UUID, int, str, or None should raise ValueError."""
        with pytest.raises(
            ValueError, match="Value must be a UUID, integer or a string"
        ):
            validate_int_for_uuid_field(value)

    def test_negative_int_raises(self) -> None:
        """A negative integer should raise because int_to_uuid uses unsigned
        bytes."""
        with pytest.raises(OverflowError):
            validate_int_for_uuid_field(-1)

    def test_consistent_int_conversion(self) -> None:
        """Converting the same integer twice should yield the same UUID."""
        assert validate_int_for_uuid_field(42) == validate_int_for_uuid_field(42)

    def test_different_ints_produce_different_uuids(self) -> None:
        """Different integers should produce different UUIDs."""
        assert validate_int_for_uuid_field(1) != validate_int_for_uuid_field(2)


# ---------------------------------------------------------------------------
# Tests for validate_str_for_uuid_field
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestValidateStrForUuidField:
    """Tests for the validate_str_for_uuid_field function."""

    def test_uuid_input_returned_as_is(self) -> None:
        """A UUID input should be returned unchanged."""
        result = validate_str_for_uuid_field(SAMPLE_UUID)
        assert result is SAMPLE_UUID

    def test_str_length_36_valid_uuid_parsed(self) -> None:
        """A valid 36-char UUID string should be parsed directly."""
        result = validate_str_for_uuid_field(SAMPLE_UUID_STR)
        assert result == SAMPLE_UUID
        assert isinstance(result, UUID)

    def test_str_length_32_valid_uuid_parsed(self) -> None:
        """A valid 32-char hex UUID string should be parsed directly."""
        result = validate_str_for_uuid_field(SAMPLE_UUID_HEX)
        assert result == SAMPLE_UUID
        assert isinstance(result, UUID)

    def test_str_length_36_invalid_uuid_falls_back_to_str_to_uuid(self) -> None:
        """A 36-char string that is NOT a valid UUID should fall back to
        str_to_uuid."""
        value = "a" * 36  # valid length but not a valid UUID
        result = validate_str_for_uuid_field(value)
        assert result == str_to_uuid(value)
        assert isinstance(result, UUID)

    def test_str_length_32_invalid_uuid_falls_back_to_str_to_uuid(self) -> None:
        """A 32-char string that is NOT a valid UUID hex should fall back to
        str_to_uuid."""
        value = "z" * 32  # 'z' is not a valid hex digit
        result = validate_str_for_uuid_field(value)
        assert result == str_to_uuid(value)
        assert isinstance(result, UUID)

    @pytest.mark.parametrize("value", ["hello", "domain_x", "short", "a" * 100])
    def test_str_other_lengths_converted_via_str_to_uuid(self, value: str) -> None:
        """Strings of lengths other than 32/36 should be converted via
        str_to_uuid."""
        result = validate_str_for_uuid_field(value)
        assert result == str_to_uuid(value)
        assert isinstance(result, UUID)

    def test_none_returns_none(self) -> None:
        """None input should return None."""
        assert validate_str_for_uuid_field(None) is None

    @pytest.mark.parametrize("value", [42, 3.14, [], {}, object()])
    def test_unsupported_type_raises_value_error(self, value: object) -> None:
        """Types other than UUID, str, or None should raise ValueError."""
        with pytest.raises(ValueError, match="Value must be a UUID or a string"):
            validate_str_for_uuid_field(value)

    def test_consistent_str_conversion(self) -> None:
        """Converting the same string twice should yield the same UUID."""
        assert validate_str_for_uuid_field("hello") == validate_str_for_uuid_field(
            "hello"
        )

    def test_different_strs_produce_different_uuids(self) -> None:
        """Different strings should produce different UUIDs."""
        assert validate_str_for_uuid_field("alpha") != validate_str_for_uuid_field(
            "beta"
        )

    def test_empty_string_converted(self) -> None:
        """An empty string (length 0) should be converted via str_to_uuid."""
        result = validate_str_for_uuid_field("")
        assert result == str_to_uuid("")
        assert isinstance(result, UUID)


# ---------------------------------------------------------------------------
# Tests for validate_str_primary_key_args
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestValidateStrPrimaryKeyArgs:
    """Tests for the validate_str_primary_key_args function."""

    def test_non_dict_input_raises_value_error(self) -> None:
        """Non-dict inputs should raise ValueError."""
        with pytest.raises(ValueError, match="Input is not a dict"):
            validate_str_primary_key_args("not_a_dict", "id", "domain_id")

    @pytest.mark.parametrize("non_dict", [42, None, [], "string", True])
    def test_non_dict_types_raise_value_error(self, non_dict: object) -> None:
        """Various non-dict types should all raise ValueError."""
        with pytest.raises(ValueError, match="Input is not a dict"):
            validate_str_primary_key_args(
                non_dict, _uuid_field_name(), _str_field_name()
            )

    def test_str_id_provided_uuid_id_absent_derives_uuid(self) -> None:
        """When str_id is provided and uuid_id is absent, uuid_id should be
        derived from str_id."""
        data: dict[str, object] = {_str_field_name(): SAMPLE_STR}
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_uuid_field_name()] == str_to_uuid(SAMPLE_STR)
        assert data[_str_field_name()] == SAMPLE_STR

    def test_str_id_provided_uuid_id_none_derives_uuid(self) -> None:
        """When str_id is provided and uuid_id is explicitly None, uuid_id
        should be derived from str_id."""
        data: dict[str, object] = {
            _uuid_field_name(): None,
            _str_field_name(): SAMPLE_STR,
        }
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_uuid_field_name()] == str_to_uuid(SAMPLE_STR)

    def test_str_id_as_uuid_field_switches_and_derives(self) -> None:
        """When a string value is provided in the uuid_id field and str_id is
        None, the value should be moved to str_id and uuid_id derived."""
        data: dict[str, object] = {
            _uuid_field_name(): SAMPLE_STR,
            _str_field_name(): None,
        }
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_str_field_name()] == SAMPLE_STR
        assert data[_uuid_field_name()] == str_to_uuid(SAMPLE_STR)

    def test_str_id_as_uuid_field_str_id_absent_switches(self) -> None:
        """When a string value is provided in the uuid_id field and str_id key
        doesn't exist at all, the value should be moved to str_id and uuid_id
        derived."""
        data: dict[str, object] = {_uuid_field_name(): SAMPLE_STR}
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_str_field_name()] == SAMPLE_STR
        assert data[_uuid_field_name()] == str_to_uuid(SAMPLE_STR)

    def test_str_id_missing_raises_value_error(self) -> None:
        """When str_id is not provided and uuid_id is not a string, should
        raise ValueError."""
        data: dict[str, object] = {_uuid_field_name(): uuid4()}
        with pytest.raises(
            ValueError, match=f"{_str_field_name()} not provided or not a string"
        ):
            validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

    def test_str_id_non_string_raises_value_error(self) -> None:
        """When str_id is not a string (e.g. int), should raise ValueError."""
        data: dict[str, object] = {_uuid_field_name(): None, _str_field_name(): 123}
        with pytest.raises(
            ValueError, match=f"{_str_field_name()} not provided or not a string"
        ):
            validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

    def test_matching_uuid_and_str_id_passes(self) -> None:
        """When uuid_id (as UUID) matches the one derived from str_id, no
        error should be raised."""
        expected_uuid = str_to_uuid(SAMPLE_STR)
        data: dict[str, object] = {
            _uuid_field_name(): expected_uuid,
            _str_field_name(): SAMPLE_STR,
        }
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_uuid_field_name()] == expected_uuid
        assert data[_str_field_name()] == SAMPLE_STR

    def test_mismatching_uuid_and_str_id_raises_value_error(self) -> None:
        """When uuid_id (as UUID) does not match the one derived from str_id,
        ValueError should be raised."""
        wrong_uuid = uuid4()
        data: dict[str, object] = {
            _uuid_field_name(): wrong_uuid,
            _str_field_name(): SAMPLE_STR,
        }
        with pytest.raises(
            ValueError, match="is not identical to the one derived from"
        ):
            validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

    def test_uuid_id_as_matching_string_passes(self) -> None:
        """When uuid_id is provided as a string representation that matches
        the UUID derived from str_id, no error should be raised. The string
        uuid_id is converted to UUID before comparison."""
        expected_uuid = str_to_uuid(SAMPLE_STR)
        data: dict[str, object] = {
            _uuid_field_name(): str(expected_uuid),
            _str_field_name(): SAMPLE_STR,
        }
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())

        assert data[_uuid_field_name()] == expected_uuid
        assert data[_str_field_name()] == SAMPLE_STR

    def test_data_mutated_in_place(self) -> None:
        """The function should mutate the input dict in place (not return a
        copy)."""
        data: dict[str, object] = {_str_field_name(): SAMPLE_STR}
        validate_str_primary_key_args(data, _uuid_field_name(), _str_field_name())
        assert _uuid_field_name() in data


# ---------------------------------------------------------------------------
# Tests for validate_int_primary_key_args
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestValidateIntPrimaryKeyArgs:
    """Tests for the validate_int_primary_key_args function."""

    def test_non_dict_input_raises_value_error(self) -> None:
        """Non-dict inputs should raise ValueError."""
        with pytest.raises(ValueError, match="Input is not a dict"):
            validate_int_primary_key_args("not_a_dict", "id", "concept_id")

    @pytest.mark.parametrize("non_dict", [42, None, [], "string", True])
    def test_non_dict_types_raise_value_error(self, non_dict: object) -> None:
        """Various non-dict types should all raise ValueError."""
        with pytest.raises(ValueError, match="Input is not a dict"):
            validate_int_primary_key_args(
                non_dict, _uuid_field_name(), _int_field_name()
            )

    @pytest.mark.parametrize("int_id", [0, 1, 42, 999_999])
    def test_int_id_provided_uuid_id_absent_derives_uuid(self, int_id: int) -> None:
        """When int_id is provided and uuid_id is absent, uuid_id should be
        derived from int_id."""
        data: dict[str, object] = {_int_field_name(): int_id}
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == int_to_uuid(int_id)
        assert data[_int_field_name()] == int_id

    def test_int_id_provided_uuid_id_none_derives_uuid(self) -> None:
        """When int_id is provided and uuid_id is explicitly None, uuid_id
        should be derived from int_id."""
        data: dict[str, object] = {
            _uuid_field_name(): None,
            _int_field_name(): SAMPLE_INT,
        }
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == int_to_uuid(SAMPLE_INT)

    def test_int_id_as_uuid_field_switches_and_derives(self) -> None:
        """When an integer value is provided in the uuid_id field and int_id
        is None, the value should be moved to int_id and uuid_id derived."""
        data: dict[str, object] = {
            _uuid_field_name(): SAMPLE_INT,
            _int_field_name(): None,
        }
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_int_field_name()] == SAMPLE_INT
        assert data[_uuid_field_name()] == int_to_uuid(SAMPLE_INT)

    def test_int_id_as_uuid_field_int_id_absent_switches(self) -> None:
        """When an integer value is provided in the uuid_id field and int_id
        key doesn't exist, the value should be moved to int_id and uuid_id
        derived."""
        data: dict[str, object] = {_uuid_field_name(): SAMPLE_INT}
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_int_field_name()] == SAMPLE_INT
        assert data[_uuid_field_name()] == int_to_uuid(SAMPLE_INT)

    def test_int_id_missing_raises_value_error(self) -> None:
        """When int_id is not provided and uuid_id is not an int, should raise
        ValueError."""
        data: dict[str, object] = {_uuid_field_name(): uuid4()}
        with pytest.raises(
            ValueError, match=f"{_int_field_name()} not provided or not an integer"
        ):
            validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

    def test_int_id_non_int_raises_value_error(self) -> None:
        """When int_id is not an integer (e.g. str), should raise ValueError."""
        data: dict[str, object] = {
            _uuid_field_name(): None,
            _int_field_name(): "not_int",
        }
        with pytest.raises(
            ValueError, match=f"{_int_field_name()} not provided or not an integer"
        ):
            validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

    def test_matching_uuid_and_int_id_passes(self) -> None:
        """When uuid_id (as UUID) matches the one derived from int_id, no
        error should be raised."""
        expected_uuid = int_to_uuid(SAMPLE_INT)
        data: dict[str, object] = {
            _uuid_field_name(): expected_uuid,
            _int_field_name(): SAMPLE_INT,
        }
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == expected_uuid
        assert data[_int_field_name()] == SAMPLE_INT

    def test_mismatching_uuid_and_int_id_raises_value_error(self) -> None:
        """When uuid_id (as UUID) does not match the one derived from int_id,
        ValueError should be raised."""
        wrong_uuid = uuid4()
        data: dict[str, object] = {
            _uuid_field_name(): wrong_uuid,
            _int_field_name(): SAMPLE_INT,
        }
        with pytest.raises(
            ValueError, match="is not identical to the one derived from"
        ):
            validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

    def test_uuid_id_as_matching_string_passes(self) -> None:
        """When uuid_id is provided as a string representation that matches
        the UUID derived from int_id, no error should be raised. The string
        uuid_id is converted to UUID before comparison."""
        expected_uuid = int_to_uuid(SAMPLE_INT)
        data: dict[str, object] = {
            _uuid_field_name(): str(expected_uuid),
            _int_field_name(): SAMPLE_INT,
        }
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == expected_uuid
        assert data[_int_field_name()] == SAMPLE_INT

    def test_mismatching_uuid_string_and_int_id_raises_value_error(self) -> None:
        """When uuid_id is a string that does NOT match the derived UUID,
        ValueError should be raised at the first string comparison."""
        wrong_uuid = uuid4()
        data: dict[str, object] = {
            _uuid_field_name(): str(wrong_uuid),
            _int_field_name(): SAMPLE_INT,
        }
        with pytest.raises(
            ValueError, match="is not identical to the one derived from"
        ):
            validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

    def test_data_mutated_in_place(self) -> None:
        """The function should mutate the input dict in place."""
        data: dict[str, object] = {_int_field_name(): SAMPLE_INT}
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())
        assert _uuid_field_name() in data

    def test_zero_int_id(self) -> None:
        """int_id of 0 should be valid and produce a deterministic UUID."""
        data: dict[str, object] = {_int_field_name(): 0}
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == int_to_uuid(0)

    def test_bool_int_id_treated_as_int(self) -> None:
        """In Python bool is a subclass of int, so True/False are accepted as
        valid int_id values by isinstance(int_id, int)."""
        data: dict[str, object] = {_int_field_name(): True}
        validate_int_primary_key_args(data, _uuid_field_name(), _int_field_name())

        assert data[_uuid_field_name()] == int_to_uuid(1)


# ---------------------------------------------------------------------------
# Tests for DataLineageMixin
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestDataLineageMixin:
    """Tests for the DataLineageMixin class.

    DataLineageMixin is a plain mixin (not a Pydantic model) that declares
    Pydantic Field descriptors. The fields are only resolved at runtime when
    the mixin is composed into a Model subclass, so we test the annotations
    and FieldInfo defaults directly.
    """

    def test_provenance_id_annotation_exists(self) -> None:
        """DataLineageMixin should declare a provenance_id annotation."""
        assert "provenance_id" in DataLineageMixin.__annotations__

    def test_source_traceback_annotation_exists(self) -> None:
        """DataLineageMixin should declare a source_traceback annotation."""
        assert "source_traceback" in DataLineageMixin.__annotations__

    def test_provenance_id_field_default_is_none(self) -> None:
        """The provenance_id Field should have a default of None."""
        field_info = DataLineageMixin.__dict__["provenance_id"]
        assert field_info.default is None

    def test_source_traceback_field_default_is_none(self) -> None:
        """The source_traceback Field should have a default of None."""
        field_info = DataLineageMixin.__dict__["source_traceback"]
        assert field_info.default is None

    def test_source_traceback_max_length(self) -> None:
        """The source_traceback Field should enforce max_length=255."""
        field_info = DataLineageMixin.__dict__["source_traceback"]
        max_len_metadata = [x for x in field_info.metadata if hasattr(x, "max_length")]
        assert len(max_len_metadata) == 1
        assert max_len_metadata[0].max_length == 255

    def test_provenance_id_annotation_is_optional_uuid(self) -> None:
        """The provenance_id annotation should allow UUID | None."""
        annotation = DataLineageMixin.__annotations__["provenance_id"]
        # Union types in modern Python: UUID | None
        assert UUID in (annotation.__args__ if hasattr(annotation, "__args__") else [])

    def test_source_traceback_annotation_is_optional_str(self) -> None:
        """The source_traceback annotation should allow str | None."""
        annotation = DataLineageMixin.__annotations__["source_traceback"]
        assert str in (annotation.__args__ if hasattr(annotation, "__args__") else [])
