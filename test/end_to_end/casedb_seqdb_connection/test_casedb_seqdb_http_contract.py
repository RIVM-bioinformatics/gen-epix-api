from collections.abc import Generator
from typing import Any
from uuid import UUID

import httpx
import pytest

from gen_epix.seqdb.services.remote_app import SeqdbRemoteApp
from test.end_to_end.casedb_seqdb_connection.contract_helpers import (
    OPENAPI_PATHS_BY_SERVICE,
    ROOT_USER_KEY,
    get_auth_code_access_token,
    get_client_credentials_access_token,
    load_expected_snapshot,
    normalize_openapi_contract,
    register_contract_clients,
)
from test.end_to_end.casedb_seqdb_connection.envvar import get_contract_env_overrides
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager

CONTRACT_OAUTH_PORT = 9002


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="session")
def oauth_server() -> Generator[ServerManager, None, None]:
    with ServerManager(
        service=ServerType.OAUTH,
        host="127.0.0.1",
        port=CONTRACT_OAUTH_PORT,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start OAuth server")
        register_contract_clients(server)
        yield server


@pytest.fixture(scope="session")
def seqdb_server(oauth_server: ServerManager) -> Generator[ServerManager, None, None]:
    with ServerManager(
        service=ServerType.SEQDB,
        host="127.0.0.1",
        port=8001,
        app_import_path="gen_epix.seqdb.app:app",
        process_env_overrides=get_contract_env_overrides(),
    ) as server:
        if not server.start():
            pytest.fail("Failed to start SeqDB contract server")
        yield server


@pytest.fixture(scope="session")
def casedb_server(
    oauth_server: ServerManager, seqdb_server: ServerManager
) -> Generator[ServerManager, None, None]:
    with ServerManager(
        service=ServerType.CASEDB,
        host="127.0.0.1",
        port=8000,
        app_import_path="gen_epix.casedb.app:app",
        process_env_overrides=get_contract_env_overrides(),
    ) as server:
        if not server.start():
            pytest.fail("Failed to start CaseDB contract server")
        yield server


@pytest.fixture(scope="session")
def casedb_root_token(
    oauth_server: ServerManager, casedb_server: ServerManager
) -> str:
    return get_auth_code_access_token(oauth_server.base_url)


@pytest.fixture(scope="session")
def seqdb_machine_token(
    oauth_server: ServerManager, seqdb_server: ServerManager
) -> str:
    return get_client_credentials_access_token(oauth_server.base_url)


@pytest.fixture(scope="session")
def contract_scenario(
    casedb_server: ServerManager, casedb_root_token: str
) -> dict[str, Any]:
    headers = _auth_headers(casedb_root_token)
    with httpx.Client(base_url=casedb_server.base_url, timeout=20.0) as client:
        ref_cols = _get_json(client, "/v1/ref_cols", headers=headers)
        cols = _get_json(client, "/v1/cols", headers=headers)
        cases = _get_json(client, "/v1/cases", headers=headers)
        return _discover_contract_scenario(
            client, headers, ref_cols, cols, cases, casedb_root_token
        )


def test_casedb_contract_positive_routes(
    casedb_server: ServerManager,
    casedb_root_token: str,
    contract_scenario: dict[str, Any],
) -> None:
    headers = _auth_headers(casedb_root_token)
    with httpx.Client(base_url=casedb_server.base_url, timeout=20.0) as client:
        phylo_response = client.post(
            "/v1/retrieve/phylogenetic_tree",
            headers=headers,
            json=contract_scenario["phylogenetic_tree_body"],
        )
        assert phylo_response.status_code == 200, phylo_response.text
        phylo_json = phylo_response.json()
        assert phylo_json["tree_algorithm_code"] == contract_scenario["tree_algorithm"]
        assert isinstance(phylo_json["newick_repr"], str)
        assert phylo_json["newick_repr"]
        assert isinstance(phylo_json.get("profile_ids"), list)

        similar_response = client.post(
            "/v1/retrieve/similar_cases",
            headers=headers,
            json=contract_scenario["similar_cases_body"],
        )
        assert similar_response.status_code == 200, similar_response.text
        similar_json = similar_response.json()
        assert isinstance(similar_json, list)
        assert similar_json
        for case_id in similar_json:
            UUID(case_id)

        fasta_response = client.post(
            "/v1/retrieve/genetic_sequence/fasta",
            data=_build_fasta_form_data(
                contract_scenario["fasta_body"], casedb_root_token
            ),
        )
        assert fasta_response.status_code == 200, fasta_response.text
        assert fasta_response.headers["content-type"].startswith("application/x-fasta")
        assert 'filename="contract.fasta"' in fasta_response.headers[
            "content-disposition"
        ]
        assert any(
            line.startswith(">")
            for line in fasta_response.text.splitlines()
            if line.strip()
        )


def test_casedb_contract_auth_errors(
    casedb_server: ServerManager, contract_scenario: dict[str, Any]
) -> None:
    with httpx.Client(base_url=casedb_server.base_url, timeout=20.0) as client:
        missing_response = client.post(
            "/v1/retrieve/similar_cases",
            json=contract_scenario["similar_cases_body"],
        )
        assert missing_response.status_code == 401

        invalid_response = client.post(
            "/v1/retrieve/similar_cases",
            headers=_auth_headers("invalid-token"),
            json=contract_scenario["similar_cases_body"],
        )
        assert invalid_response.status_code == 401


def test_casedb_contract_validation_errors(
    casedb_server: ServerManager, casedb_root_token: str
) -> None:
    headers = _auth_headers(casedb_root_token)
    with httpx.Client(base_url=casedb_server.base_url, timeout=20.0) as client:
        json_error = client.post(
            "/v1/retrieve/similar_cases",
            headers=headers,
            json={},
        )
        assert json_error.status_code == 422, json_error.text
        _assert_fastapi_validation_error(json_error.json())

        form_error = client.post(
            "/v1/retrieve/genetic_sequence/fasta",
            data={"token": casedb_root_token},
        )
        assert form_error.status_code == 422, form_error.text
        _assert_fastapi_validation_error(form_error.json())


@pytest.mark.parametrize(
    ("route", "body"),
    [
        ("/v1/retrieve/phylogenetic_tree", {}),
        ("/v1/retrieve/similar_profiles", {}),
        ("/v1/retrieve/seq_fasta", {}),
    ],
)
def test_seqdb_contract_validation_errors(
    seqdb_server: ServerManager,
    seqdb_machine_token: str,
    route: str,
    body: dict[str, Any],
) -> None:
    with httpx.Client(base_url=seqdb_server.base_url, timeout=20.0) as client:
        response = client.post(route, headers=_auth_headers(seqdb_machine_token), json=body)
        assert response.status_code == 422, response.text
        _assert_fastapi_validation_error(response.json())


@pytest.mark.parametrize("service_name", ["casedb", "seqdb"])
def test_openapi_contract_snapshots(
    casedb_server: ServerManager,
    seqdb_server: ServerManager,
    service_name: str,
) -> None:
    assert service_name in {"casedb", "seqdb"}
    server = casedb_server if service_name == "casedb" else seqdb_server
    with httpx.Client(base_url=server.base_url, timeout=20.0) as client:
        response = client.get("/openapi.json")
        response.raise_for_status()
        openapi_doc = response.json()
    actual = normalize_openapi_contract(
        openapi_doc, OPENAPI_PATHS_BY_SERVICE[service_name]
    )
    expected = load_expected_snapshot(service_name)
    assert actual == expected


def test_seqdb_remote_routes_match_live_openapi(seqdb_server: ServerManager) -> None:
    selected_routes = {
        f"/v1{route}"
        for route in SeqdbRemoteApp.ROUTE_MAP.values()
        if f"/v1{route}" in set(OPENAPI_PATHS_BY_SERVICE["seqdb"])
    }
    with httpx.Client(base_url=seqdb_server.base_url, timeout=20.0) as client:
        response = client.get("/openapi.json")
        response.raise_for_status()
        openapi_doc = response.json()
    assert selected_routes.issubset(set(openapi_doc["paths"]))


def _discover_contract_scenario(
    client: httpx.Client,
    headers: dict[str, str],
    ref_cols: list[dict[str, Any]],
    cols: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    casedb_root_token: str,
) -> dict[str, Any]:
    ref_col_by_id = {ref_col["id"]: ref_col for ref_col in ref_cols}
    col_by_id = {col["id"]: col for col in cols}

    phylo_body: dict[str, Any] | None = None
    similar_body: dict[str, Any] | None = None
    tree_algorithm: str | None = None
    for col in col_by_id.values():
        ref_col = ref_col_by_id.get(col["ref_col_id"])
        if ref_col is None or ref_col.get("col_type") != "GENETIC_DISTANCE":
            continue
        case_ids = [
            case["id"]
            for case in cases
            if case["content"].get(col["id"])
            and case.get("case_type_id") == col.get("case_type_id")
        ]
        if len(case_ids) < 2:
            continue
        tree_algorithm_codes = col.get("tree_algorithm_codes") or []
        if not tree_algorithm_codes:
            continue
        tree_algorithm = tree_algorithm_codes[0]
        selected_case_ids = case_ids[:5]
        candidate_phylo_body = {
            "case_type_id": col["case_type_id"],
            "genetic_distance_col_id": col["id"],
            "tree_algorithm_code": tree_algorithm,
            "case_ids": selected_case_ids,
        }
        candidate_similar_body = {
            "case_type_id": col["case_type_id"],
            "genetic_distance_col_id": col["id"],
            "max_distance": 5,
            "case_ids": selected_case_ids,
        }
        if phylo_body is None:
            phylo_body = candidate_phylo_body

        similar_response = client.post(
            "/v1/retrieve/similar_cases",
            headers=headers,
            json=candidate_similar_body,
        )
        if similar_response.status_code == 200 and similar_response.json():
            similar_body = candidate_similar_body
            break

    fasta_body: dict[str, Any] | None = None
    for col in col_by_id.values():
        ref_col = ref_col_by_id.get(col["ref_col_id"])
        if ref_col is None or ref_col.get("col_type") != "GENETIC_SEQUENCE":
            continue
        case_ids = [
            case["id"]
            for case in cases
            if case["content"].get(col["id"])
            and case.get("case_type_id") == col.get("case_type_id")
        ]
        if not case_ids:
            continue
        fasta_body = {
            "case_type_id": col["case_type_id"],
            "genetic_sequence_col_id": col["id"],
            "case_ids": case_ids[:5],
            "file_name": "contract.fasta",
        }
        break

    if not phylo_body or not similar_body or not fasta_body or not tree_algorithm:
        raise AssertionError(
            "Unable to discover a valid HTTP-only CASEDB contract scenario"
        )

    return {
        "phylogenetic_tree_body": phylo_body,
        "similar_cases_body": similar_body,
        "fasta_body": fasta_body,
        "tree_algorithm": tree_algorithm,
        "root_user_key": ROOT_USER_KEY,
        "token_preview": casedb_root_token[:20],
    }


def _get_json(
    client: httpx.Client, route: str, headers: dict[str, str]
) -> list[dict[str, Any]]:
    response = client.get(route, headers=headers)
    response.raise_for_status()
    payload = response.json()
    assert isinstance(payload, list)
    return payload


def _build_fasta_form_data(
    fasta_body: dict[str, Any], casedb_root_token: str
) -> dict[str, Any]:
    return {
        "token": casedb_root_token,
        "case_type_id": str(fasta_body["case_type_id"]),
        "genetic_sequence_col_id": str(fasta_body["genetic_sequence_col_id"]),
        "file_name": str(fasta_body["file_name"]),
        "case_ids": [str(case_id) for case_id in fasta_body["case_ids"]],
    }


def _assert_fastapi_validation_error(payload: dict[str, Any]) -> None:
    assert payload["detail"]
    assert isinstance(payload["detail"], list)
    first_issue = payload["detail"][0]
    assert "loc" in first_issue
    assert "msg" in first_issue
    assert "type" in first_issue
