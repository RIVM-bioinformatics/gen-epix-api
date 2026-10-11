"""Unit tests for gen_epix.casedb.config.cfg_types."""

from typing import Any

import pytest

from gen_epix.casedb.config import cfg_types
from gen_epix.casedb.config.cfg import CasedbAppCfg
from gen_epix.commondb.config import cfg_types as commondb_cfg_types

SEQDB_LOCAL_USER_KEYS = {"id", "key", "organization_id", "roles"}
SEQDB_REMOTE_KEYS = {
    "module",
    "class_name",
    "protocol",
    "host",
    "port",
    "auth_protocol",
    "oauth_flow",
    "oauth_client_id",
    "oauth_client_secret",
    "oauth_scope",
    "oauth_discovery_url",
}
CASEDB_SERVICE_KEYS = {"case", "geo", "ontology", "seqdb"}


def _all_keys(typed_dict: type) -> set[str]:
    """Return required and optional keys; NotRequired is not runtime-reliable here."""
    return set(typed_dict.__required_keys__) | set(  # type: ignore[attr-defined]
        typed_dict.__optional_keys__  # type: ignore[attr-defined]
    )


def _seqdb_default_props() -> dict[str, Any]:
    """Return casedb's default seqdb service props."""
    return CasedbAppCfg.DEFAULT_SETTINGS["service"]["seqdb"]["props"]


@pytest.mark.parametrize(
    "typed_dict, expected_keys",
    [
        pytest.param(
            cfg_types.SeqdbClientLocalUserDict,
            SEQDB_LOCAL_USER_KEYS,
            id="local_user",
        ),
        pytest.param(cfg_types.SeqdbClientLocalDict, {"user"}, id="local_client"),
        pytest.param(
            cfg_types.SeqdbClientRemoteDict,
            SEQDB_REMOTE_KEYS,
            id="remote_client",
        ),
        pytest.param(
            cfg_types.SeqdbClientPropsDict,
            {"seqdb_client_type", "local_client", "remote_client"},
            id="client_props",
        ),
        pytest.param(
            cfg_types.SeqdbClientEntryDict,
            {"module", "class_name", "props"},
            id="client_entry",
        ),
        pytest.param(
            cfg_types.ResolvedCasedbServiceSectionDict,
            CASEDB_SERVICE_KEYS
            | _all_keys(commondb_cfg_types.ResolvedServiceSectionDict),
            id="resolved_service_section",
        ),
        pytest.param(
            cfg_types.CasedbAppCfgSettingsDict,
            {"app", "api", "log", "feature_flags", "service", "repository"},
            id="settings",
        ),
        pytest.param(
            cfg_types.ResolvedCasedbAppCfgSettingsDict,
            {"app", "api", "log", "feature_flags", "service", "repository"},
            id="resolved_settings",
        ),
    ],
)
def test_typed_dict_keys(typed_dict: type, expected_keys: set[str]) -> None:
    """Each TypedDict declares exactly the expected keys."""
    assert _all_keys(typed_dict) == expected_keys


def test_service_section_extends_base_without_dropping_keys() -> None:
    """The casedb service section adds its keys on top of the base ones."""
    base_keys = _all_keys(commondb_cfg_types.ServiceSectionDict)

    assert _all_keys(cfg_types.CasedbServiceSectionDict) == (
        base_keys | CASEDB_SERVICE_KEYS
    )


def test_instances_are_plain_dicts() -> None:
    """TypedDicts construct ordinary dicts at runtime."""
    user: cfg_types.SeqdbClientLocalUserDict = {
        "id": "i",
        "key": "k",
        "organization_id": "o",
        "roles": [],
    }

    assert isinstance(user, dict)
    assert cfg_types.SeqdbClientLocalDict(user=user) == {"user": user}


def test_default_seqdb_props_match_typed_dict_keys() -> None:
    """Default seqdb props mirror the seqdb TypedDict shapes."""
    props = _seqdb_default_props()

    assert set(props) == _all_keys(cfg_types.SeqdbClientPropsDict)
    assert set(props["local_client"]["user"]) == SEQDB_LOCAL_USER_KEYS
    assert set(props["remote_client"]) == SEQDB_REMOTE_KEYS


def test_default_service_section_covers_casedb_service_keys() -> None:
    """Default settings configure every casedb-specific service."""
    service_keys = set(CasedbAppCfg.DEFAULT_SETTINGS["service"])

    assert CASEDB_SERVICE_KEYS <= service_keys
