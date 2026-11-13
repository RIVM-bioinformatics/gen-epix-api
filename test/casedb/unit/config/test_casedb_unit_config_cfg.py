"""Tests for casedb application configuration behavior."""

import pytest
from dynaconf.validator import ValidationError, Validator

from gen_epix.casedb.config.cfg import CasedbAppCfg
from gen_epix.casedb.domain.enum import FeatureFlag


@pytest.fixture(name="disable_upload_validator")
def make_disable_upload_validator() -> Validator:
    """Return the validator for casedb's disable-upload feature flag."""
    # pylint: disable=protected-access
    validators = object.__new__(CasedbAppCfg)._get_feature_flag_validators()
    name = f"feature_flags.{FeatureFlag.DISABLE_UPLOAD.value}"
    return next(validator for validator in validators if validator.names == (name,))


@pytest.mark.parametrize(
    "value",
    [False, True, "0", "1", "false", "true", "FALSE", "TRUE"],
)
def test_disable_upload_validator_accepts_bool_like_values(
    disable_upload_validator: Validator, value: bool | str
) -> None:
    """Accept booleans and the shared config's supported boolean strings."""
    disable_upload_validator.validate(
        {f"feature_flags.{FeatureFlag.DISABLE_UPLOAD.value}": value}
    )


@pytest.mark.parametrize("value", ["yes", "", None, 0, 1])
def test_disable_upload_validator_rejects_other_values(
    disable_upload_validator: Validator, value: object
) -> None:
    """Reject values outside the documented bool-like config forms."""
    with pytest.raises(ValidationError):
        disable_upload_validator.validate(
            {f"feature_flags.{FeatureFlag.DISABLE_UPLOAD.value}": value}
        )
