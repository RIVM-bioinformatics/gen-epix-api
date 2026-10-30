"""Exercise the PPR sharing and membership contracts through a composed app."""

import asyncio
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient
from typing import Any, get_args
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI, Request

from gen_epix.casedb.api.router import create_routers
from gen_epix.casedb.config import CasedbAppCfg
from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.domain.util import set_env_variables
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import UuidSetFilter
from gen_epix.seqdb.config import SeqdbAppCfg

pytestmark = pytest.mark.integration


@pytest.fixture(
    scope="module",
    params=[DevRepositoryConfig.DICT_EMPTY, DevRepositoryConfig.SA_SQLITE_EMPTY],
)
def authorization_env(request, tmp_path_factory):
    """Use real repositories, RBAC, policy registration and ABAC resolution."""
    directory = tmp_path_factory.mktemp(f"case_set_auth_{request.param.value}")
    with pytest.MonkeyPatch.context() as monkeypatch:
        for app_name in ("CASEDB", "SEQDB"):
            for suffix in ("SETTINGS_FILES", "LOG_CONFIG_FILE"):
                key = f"{app_name}_{suffix}"
                monkeypatch.setenv(key, "")
        set_env_variables(
            AppType.CASEDB,
            DevIdpConfig.NONE,
            request.param,
            extra_settings_files=[Path("test/test_client/settings.toml")],
        )
        seqdb_cfg = SeqdbAppCfg(log_any=False)
        casedb_cfg = CasedbAppCfg(log_any=False)
        casedb_cfg.cfg["service"]["seqdb"]["props"]["local_client"][
            "app_cfg"
        ] = seqdb_cfg
        casedb_cfg.copy_repository_files(directory)
        seqdb_cfg.copy_repository_files(directory)
        env = CasedbTestClient("case_set_authorization", directory, casedb_cfg)

    root = env.get_root_user()
    env.set_obj(root)
    for index, name in ((2, "uploader"), (3, "consumer"), (4, "outsider")):
        organization = env.create_organization(root, f"org{index}")
        env.set_obj(
            env.app.handle(
                command.UserCrudCommand(
                    user=root,
                    operation=CrudOperation.CREATE_ONE,
                    objs=model.User(
                        key=f"{name}@example.invalid",
                        name=name,
                        organization_id=organization.id,
                        roles={enum.Role.ORG_USER.value},
                        is_active=True,
                    ),
                )
            )
        )
    for index in range(1, 5):
        env.create_data_collection(root, f"data_collection{index}")
    env.create_case_type(root, "case_type1", None, None)
    env.create_case_type(root, "case_type2", None, None)
    env.create_case_type_set_category(root, "category")
    env.create_case_type_set(
        root, "case_types", {"case_type1", "case_type2"}, "category"
    )
    env.create_ref_dim(root, "ref_dim1", enum.DimType.OTHER)
    env.create_ref_col(root, "ref_col1_1")
    env.create_dim(root, "dim1_1_1")
    env.create_col(root, "col1_1_1_1")
    env.create_col_set(root, "columns", {"col1_1_1_1"})
    env.create_case_set_category(root, "Outbreak")
    env.create_case_set_status(root, "Open")

    # Collections 1/2 are private uploader/consumer origins; 3 is national.
    # Collection 4 is readable but has no organization add grant.
    for user_name, organization_index, private_index in (
        ("uploader", 2, 1),
        ("consumer", 3, 2),
    ):
        for collection_index in (private_index, 3, 4):
            private = collection_index == private_index
            env.create_organization_access_case_policy(
                root,
                f"policy{organization_index}_{collection_index}",
                "case_types",
                is_private=private,
                add_case=private or (user_name == "uploader" and collection_index == 3),
                remove_case=private,
                read_col_set_or_str="columns",
                write_col_set_or_str="columns" if private else None,
                add_case_set=private or collection_index == 3,
                remove_case_set=private,
            )
            env.create_user_access_case_policy(
                root,
                user_name,
                f"data_collection{collection_index}",
                "case_types",
                read_col_set_or_str="columns",
                write_col_set_or_str="columns",
            )
    env.set_obj(
        env.app.handle(
            command.UserCrudCommand(
                user=root,
                operation=CrudOperation.CREATE_ONE,
                objs=model.User(
                    key="reader@example.invalid",
                    name="reader",
                    is_active=True,
                    organization_id=env.get_obj(model.Organization, "org3").id,
                    roles={enum.Role.ORG_USER.value},
                ),
            )
        )
    )
    env.create_user_access_case_policy(
        root,
        "reader",
        "data_collection3",
        "case_types",
        read_col_set_or_str="columns",
        write_case_set=False,
    )
    return env


def _create_case(env, case_type_name="case_type1"):
    """Seed a case with the uploader's private origin."""
    return env.app.handle(
        command.CaseCrudCommand(
            user=env.get_root_user(),
            operation=CrudOperation.CREATE_ONE,
            objs=model.Case(
                case_type_id=env.get_obj(model.CaseType, case_type_name).id,
                created_in_data_collection_id=env.get_obj(
                    model.DataCollection, "data_collection1"
                ).id,
                content={},
            ),
        )
    )


async def _authenticated_user(request: Request) -> model.User:
    """Supply a persisted test identity while retaining all command policies."""
    return request.app.state.authorization_env.get_obj(
        model.User, request.headers["x-test-user"]
    )


def _create_api(env) -> FastAPI:
    api = create_fast_api(env.app, create_routers_fn=create_routers, debug=True)
    api.state.authorization_env = env
    security = get_args(env.app.impl.registered_user_dependency)[1]
    api.dependency_overrides[security.dependency] = _authenticated_user
    return api


async def _post(client, user, path, body, status=200) -> Any:
    response = await client.post(
        f"/v1/{path}", json=body, headers={"x-test-user": user}
    )
    assert response.status_code == status, response.text
    return response.json()


def _query(key, identifiers, invert=False):
    return {"type": "UUID_SET", "key": key, "members": identifiers, "invert": invert}


def test_http_sharing_and_membership_lifecycle(authorization_env):
    asyncio.run(_sharing_and_membership_lifecycle(authorization_env))


def test_http_case_set_access_through_created_in_collection(authorization_env):
    asyncio.run(_case_set_access_through_created_in_collection(authorization_env))


async def _case_set_access_through_created_in_collection(env):
    api = _create_api(env)
    case = _create_case(env)
    origin = str(env.get_obj(model.DataCollection, "data_collection2").id)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=api), base_url="http://test"
    ) as client:
        # Creating in a single collection stores no CaseSetDataCollectionLink:
        # the creating collection is dropped from data_collection_ids.
        created = await _post(
            client,
            "consumer",
            "create/case_set",
            {
                "case_ids": [str(case.id)],
                "data_collection_ids": [origin],
                "case_set": {
                    "case_type_id": str(case.case_type_id),
                    "created_in_data_collection_id": origin,
                    "case_set_category_id": str(
                        env.get_obj(model.CaseSetCategory, "Outbreak").id
                    ),
                    "case_set_status_id": str(
                        env.get_obj(model.CaseSetStatus, "Open").id
                    ),
                    "name": str(uuid4()),
                    "code": str(uuid4()),
                    "description": "Created-in collection access regression",
                },
            },
        )
        case_set_id = created["id"]
        assert (
            await _post(
                client,
                "consumer",
                "case_set_data_collection_links/query",
                _query("case_set_id", [case_set_id]),
            )
            == []
        )

        # The creating collection grants read and write access.
        response = await client.get(
            f"/v1/case_sets/{case_set_id}", headers={"x-test-user": "consumer"}
        )
        assert response.status_code == 200, response.text
        assert response.json()["id"] == case_set_id
        response = await client.get(
            "/v1/case_sets", headers={"x-test-user": "consumer"}
        )
        assert response.status_code == 200, response.text
        assert case_set_id in {item["id"] for item in response.json()}
        updated = created | {"description": "Updated by owner"}
        response = await client.put(
            f"/v1/case_sets/{case_set_id}",
            json=updated,
            headers={"x-test-user": "consumer"},
        )
        assert response.status_code == 200, response.text

        # Without access to the creating collection, reads and updates are denied
        # by the PEP rather than skipped or failing on an empty result.
        response = await client.get(
            f"/v1/case_sets/{case_set_id}", headers={"x-test-user": "outsider"}
        )
        assert response.status_code == 403, response.text
        response = await client.get(
            "/v1/case_sets", headers={"x-test-user": "outsider"}
        )
        assert response.status_code == 200, response.text
        assert case_set_id not in {item["id"] for item in response.json()}
        response = await client.put(
            f"/v1/case_sets/{case_set_id}",
            json=created | {"description": "Updated by outsider"},
            headers={"x-test-user": "outsider"},
        )
        assert response.status_code == 403, response.text
        assert (
            env.app.handle(
                command.CaseSetCrudCommand(
                    user=env.get_root_user(),
                    operation=CrudOperation.READ_ONE,
                    obj_ids=case_set_id,
                )
            ).description
            == "Updated by owner"
        )

        # A case set that does not exist is reported as invalid, not as a 500.
        response = await client.get(
            f"/v1/case_sets/{uuid4()}", headers={"x-test-user": "consumer"}
        )
        assert response.status_code == 422, response.text


async def _sharing_and_membership_lifecycle(env):
    api = _create_api(env)
    first_case, second_case, private_case = (_create_case(env) for _ in range(3))
    target = str(env.get_obj(model.DataCollection, "data_collection3").id)
    forbidden_target = str(env.get_obj(model.DataCollection, "data_collection4").id)
    origin = str(env.get_obj(model.DataCollection, "data_collection2").id)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=api), base_url="http://test"
    ) as client:
        first_link = [{"case_id": str(first_case.id), "data_collection_id": target}]
        await _post(
            client,
            "uploader",
            "case_data_collection_links/batch",
            first_link,
            status=201,
        )
        assert (
            await _post(
                client,
                "consumer",
                "case_set_members/query",
                _query("case_id", [str(first_case.id)]),
            )
            == []
        )
        created = await _post(
            client,
            "consumer",
            "create/case_set",
            {
                "case_ids": [str(first_case.id)],
                "data_collection_ids": [target],
                "case_set": {
                    "case_type_id": str(first_case.case_type_id),
                    "created_in_data_collection_id": origin,
                    "case_set_category_id": str(
                        env.get_obj(model.CaseSetCategory, "Outbreak").id
                    ),
                    "case_set_status_id": str(
                        env.get_obj(model.CaseSetStatus, "Open").id
                    ),
                    "name": str(uuid4()),
                    "code": str(uuid4()),
                    "description": "PPR authorization regression",
                },
            },
        )
        case_set_id = created["id"]
        assert created["created_in_data_collection_id"] == origin
        # An inaccessible case remains invisible even in a readable CaseSet.
        env.app.handle(
            command.CaseSetMemberCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetMember(
                    case_id=private_case.id, case_set_id=case_set_id
                ),
            )
        )
        selection = _query("case_set_id", [case_set_id])
        members = await _post(client, "consumer", "case_set_members/query", selection)
        assert [member["case_id"] for member in members] == [str(first_case.id)]
        assert (
            await _post(client, "outsider", "case_set_members/query", selection) == []
        )
        links = await _post(
            client, "consumer", "case_set_data_collection_links/query", selection
        )
        assert [link["data_collection_id"] for link in links] == [target]

        # A target grant alone cannot share a case without source write access.
        second_link = {"case_id": str(second_case.id), "data_collection_id": target}
        await _post(
            client,
            "consumer",
            "case_data_collection_links/batch",
            [second_link],
            status=403,
        )
        # Validate every target before writing any item of a mixed batch.
        await _post(
            client,
            "uploader",
            "case_data_collection_links/batch",
            [
                second_link,
                {
                    "case_id": str(second_case.id),
                    "data_collection_id": forbidden_target,
                },
            ],
            status=403,
        )
        assert (
            env.app.handle(
                command.CaseDataCollectionLinkCrudCommand(
                    user=env.get_root_user(),
                    operation=CrudOperation.READ_ALL,
                    query_filter=UuidSetFilter(key="case_id", members={second_case.id}),
                )
            )
            == []
        )
        await _post(
            client,
            "uploader",
            "case_data_collection_links/batch",
            [second_link],
            status=201,
        )
        new_member = {"case_id": str(second_case.id), "case_set_id": case_set_id}
        # Reader shares the consumer organization; its user policy denies writing.
        await _post(
            client, "reader", "case_set_members/batch", [new_member], status=403
        )
        await _post(
            client,
            "consumer",
            "case_set_members/batch",
            [new_member, {"case_id": str(private_case.id), "case_set_id": case_set_id}],
            status=403,
        )
        assert (
            env.app.handle(
                command.CaseSetMemberCrudCommand(
                    user=env.get_root_user(),
                    operation=CrudOperation.READ_ALL,
                    query_filter=UuidSetFilter(key="case_id", members={second_case.id}),
                )
            )
            == []
        )
        wrong_type_case = _create_case(env, "case_type2")
        # Access is denied before the type of an inaccessible case is checked.
        await _post(
            client,
            "consumer",
            "case_set_members/batch",
            [{"case_id": str(wrong_type_case.id), "case_set_id": case_set_id}],
            status=403,
        )
        await _post(
            client,
            "consumer",
            "case_set_members/batch",
            [new_member],
            status=201,
        )
        members = await _post(client, "consumer", "case_set_members/query", selection)
        assert {member["case_id"] for member in members} == {
            str(first_case.id),
            str(second_case.id),
        }
        # The UI selects members to remove with an AND of a case and a CaseSet.
        member_selection = {
            "type": "COMPOSITE",
            "operator": "AND",
            "filters": [
                _query("case_id", [str(second_case.id)]),
                _query("case_set_id", [case_set_id]),
            ],
        }
        selected = await _post(
            client, "consumer", "case_set_members/query", member_selection
        )
        assert [member["case_id"] for member in selected] == [str(second_case.id)]
        assert (
            await _post(client, "outsider", "case_set_members/query", member_selection)
            == []
        )
        await _post(
            client,
            "consumer",
            "case_set_members/query",
            {
                "type": "COMPOSITE",
                "operator": "OR",
                "filters": [
                    _query("case_id", [str(second_case.id)]),
                    _query("id", [case_set_id]),
                ],
            },
            status=403,
        )
        # Explicit membership-record ID reads still enforce the same permissions.
        assert (
            env.app.handle(
                command.CaseSetMemberCrudCommand(
                    user=env.get_obj(model.User, "outsider"),
                    operation=CrudOperation.READ_SOME,
                    obj_ids=[member["id"] for member in members],
                )
            )
            == []
        )
        for key, invert in (("case_id", True), ("case_set_id", True), ("id", False)):
            await _post(
                client,
                "consumer",
                "case_set_members/query",
                _query(key, [case_set_id], invert),
                status=403,
            )
        for path in ("case_set_members", "case_set_data_collection_links"):
            response = await client.get(
                f"/v1/{path}", headers={"x-test-user": "consumer"}
            )
            assert response.status_code == 403, response.text
