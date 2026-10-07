from __future__ import annotations

import pytest

from gen_epix.commondb.domain.enum import FeatureFlag
from gen_epix.fastapp.app import App


@pytest.mark.parametrize(
    "query_key",
    [
        pytest.param("ALLOW_DELETE_ALL_OPERATIONAL_DATA", id="uppercase"),
        pytest.param("allow_delete_all_operational_data", id="lowercase"),
        pytest.param("Allow_Delete_All_Operational_Data", id="mixed-case"),
    ],
)
def test_get_feature_flag_matches_string_keys_without_regard_to_case(
    query_key: str,
) -> None:
    """Match string feature-flag keys without regard to case."""
    app = App(logger=None)
    app.set_feature_flag("allow_delete_all_operational_data", True)

    assert app.get_feature_flag(query_key) is True


def test_get_feature_flag_uses_exact_enum_keys() -> None:
    """Look up enum-keyed feature flags by their enum member."""
    app = App(
        logger=None,
        feature_flags={FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA: True},
    )

    assert app.get_feature_flag(FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA) is True
    assert app.get_feature_flag("ALLOW_DELETE_ALL_OPERATIONAL_DATA") is False


def test_get_feature_flag_uses_default_when_string_key_is_missing() -> None:
    """Return the caller's default when no normalized string key is present."""
    app = App(logger=None)

    assert app.get_feature_flag("missing") is False
    assert app.get_feature_flag("missing", default=True) is True
