import base64
import json
import urllib.parse
from pathlib import Path
from typing import Any

import httpx

from test.test_client.server_manager import ServerManager

CASEDB_HTTP_CLIENT_ID = "CONTRACT_CASEDB_HTTP"
CASEDB_HTTP_CLIENT_SECRET = "CONTRACT_CASEDB_HTTP_SECRET"
SEQDB_MACHINE_CLIENT_ID = "root@dummy.org"
SEQDB_MACHINE_CLIENT_SECRET = "ROOT_DUMMY_ORG_SECRET"
CASEDB_AUTH_REDIRECT_URI = "http://127.0.0.1:9100/callback"
ROOT_USER_KEY = "root@dummy.org"
OPENAPI_PATHS_BY_SERVICE = {
    "casedb": [
        "/v1/retrieve/phylogenetic_tree",
        "/v1/retrieve/similar_cases",
        "/v1/retrieve/genetic_sequence/fasta",
    ],
    "seqdb": [
        "/v1/retrieve/phylogenetic_tree",
        "/v1/retrieve/similar_profiles",
        "/v1/retrieve/seq_fasta",
    ],
}
SNAPSHOT_FILES = {
    "casedb": Path(__file__).with_name("contract.casedb.openapi.snapshot.json"),
    "seqdb": Path(__file__).with_name("contract.seqdb.openapi.snapshot.json"),
}


def register_contract_clients(oauth_server: ServerManager) -> None:
    clients = [
        {
            "client_id": CASEDB_HTTP_CLIENT_ID,
            "client_secret": CASEDB_HTTP_CLIENT_SECRET,
            "audience": "CASEDB",
            "scopes": ["openid", "profile"],
            "grant_types": ["authorization_code"],
            "redirect_uris": [CASEDB_AUTH_REDIRECT_URI],
        },
        {
            "client_id": SEQDB_MACHINE_CLIENT_ID,
            "client_secret": SEQDB_MACHINE_CLIENT_SECRET,
            "audience": "SEQDB",
            "scopes": ["openid", "profile"],
            "grant_types": ["client_credentials"],
            "redirect_uris": [],
        },
    ]
    for client in clients:
        created = oauth_server.add_client(**client)
        if not created:
            raise RuntimeError(f"Failed to register OAuth client {client['client_id']}")


def get_auth_code_access_token(
    base_url: str,
    client_id: str = CASEDB_HTTP_CLIENT_ID,
    client_secret: str = CASEDB_HTTP_CLIENT_SECRET,
    redirect_uri: str = CASEDB_AUTH_REDIRECT_URI,
    user_id: str = ROOT_USER_KEY,
    scope: str = "openid profile",
) -> str:
    authorize_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": "contract-http-state",
        "user_id": user_id,
    }
    with httpx.Client(timeout=10.0, follow_redirects=False) as client:
        response = client.get(f"{base_url}/oauth/authorize", params=authorize_params)
        if response.status_code != 302:
            response.raise_for_status()
        location = response.headers["location"]

    query = urllib.parse.parse_qs(urllib.parse.urlparse(location).query)
    code = query["code"][0]
    form_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.post(f"{base_url}/oauth/token", data=form_data)
        response.raise_for_status()
        return response.json()["access_token"]


def get_client_credentials_access_token(
    base_url: str,
    client_id: str = SEQDB_MACHINE_CLIENT_ID,
    client_secret: str = SEQDB_MACHINE_CLIENT_SECRET,
    scope: str = "openid profile",
) -> str:
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{base_url}/oauth/token",
            data=f"grant_type=client_credentials&scope={urllib.parse.quote(scope)}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()["access_token"]


def load_expected_snapshot(service_name: str) -> dict[str, Any]:
    with SNAPSHOT_FILES[service_name].open("rt", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_openapi_contract(
    openapi_doc: dict[str, Any], selected_paths: list[str]
) -> dict[str, Any]:
    selected_path_map = {
        path: _normalize_json(openapi_doc["paths"][path])
        for path in selected_paths
        if path in openapi_doc["paths"]
    }
    refs = _collect_schema_refs(selected_path_map)
    components = openapi_doc.get("components", {}).get("schemas", {})
    selected_components: dict[str, Any] = {}
    while refs:
        schema_name = refs.pop()
        if schema_name in selected_components or schema_name not in components:
            continue
        normalized_schema = _normalize_json(components[schema_name])
        selected_components[schema_name] = normalized_schema
        refs.update(_collect_schema_refs(normalized_schema))
    return {
        "paths": selected_path_map,
        "components": {"schemas": dict(sorted(selected_components.items()))},
    }


def _collect_schema_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            refs.add(ref.rsplit("/", 1)[-1])
        for nested_value in value.values():
            refs.update(_collect_schema_refs(nested_value))
    elif isinstance(value, list):
        for nested_value in value:
            refs.update(_collect_schema_refs(nested_value))
    return refs


def _normalize_json(value: Any) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, nested_value in sorted(value.items()):
            if key in {
                "description",
                "summary",
                "title",
                "operationId",
                "examples",
                "example",
            }:
                continue
            normalized[key] = _normalize_json(nested_value)
        return normalized
    if isinstance(value, list):
        return [_normalize_json(item) for item in value]
    return value
