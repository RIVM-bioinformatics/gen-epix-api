"""Verify that synchronous command handling does not block other API requests."""

import logging
import threading
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from typing import Any

import pytest

from gen_epix.commondb.domain import command, enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.services.abac import AbacService
from gen_epix.commondb.test.test_client import TestClient as Env

TEST_TYPE = "FASTAPP_UNIT_ENDPOINT_CONCURRENCY"
WAIT_TIMEOUT = 10.0

APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


def test_blocked_command_does_not_block_independent_request(mocker: Any) -> None:
    """Allow a second request while the first request waits in ``App.handle``."""
    entered_event = threading.Event()
    release_event = threading.Event()

    def block_organization_admin_retrieval(cmd: Any) -> list[Any]:
        del cmd
        entered_event.set()
        assert release_event.wait(timeout=WAIT_TIMEOUT)
        return []

    mocker.patch.object(
        AbacService,
        "retrieve_organization_admin_name_emails",
        side_effect=block_organization_admin_retrieval,
    )

    app_cfg = APP_CFGS[f"{TEST_TYPE}__{DevRepositoryConfig.SA_SQLITE_EMPTY.value}"]
    env: Env = commondb_get_test_client(
        test_type=TEST_TYPE,
        app_cfg=app_cfg,
        verbose=False,
        log_level=logging.ERROR,
        use_endpoints=True,
    )
    assert env.endpoint_test_client is not None
    test_client = env.endpoint_test_client.test_client
    request_a_result: dict[str, Any] = {}

    def request_a() -> None:
        request_a_result["response"] = test_client.get(
            "/v1/retrieve_organization_admin_name_emails",
            timeout=WAIT_TIMEOUT,
        )

    with test_client:
        request_a_thread = threading.Thread(target=request_a)
        request_a_thread.start()
        try:
            assert entered_event.wait(timeout=WAIT_TIMEOUT)

            response_b = test_client.get("/v1/health", timeout=WAIT_TIMEOUT)

            assert response_b.status_code == 200
            assert response_b.json() == {"status": "HEALTHY"}
            assert request_a_thread.is_alive()
        finally:
            release_event.set()
            request_a_thread.join(timeout=WAIT_TIMEOUT)

    assert not request_a_thread.is_alive()
    response_a = request_a_result["response"]
    assert response_a.status_code == 200
    assert response_a.json() == []


@pytest.mark.parametrize(
    ("blocked_path", "blocked_command", "other_path"),
    [
        (
            "/v1/retrieve_organization_admin_name_emails",
            command.RetrieveOrganizationAdminNameEmailsCommand,
            "/v1/organizations",
        ),
        (
            "/v1/organizations",
            command.OrganizationCrudCommand,
            "/v1/retrieve_organization_admin_name_emails",
        ),
    ],
    ids=["custom-blocked", "crud-blocked"],
)
def test_command_requests_overlap(
    mocker: Any, blocked_path: str, blocked_command: type, other_path: str
) -> None:
    """Complete another command while a custom or CRUD command is waiting."""
    entered_event = threading.Event()
    release_event = threading.Event()
    other_finished = threading.Event()
    responses: dict[str, Any] = {}

    app_cfg = APP_CFGS[f"{TEST_TYPE}__{DevRepositoryConfig.DICT_EMPTY.value}"]
    env: Env = commondb_get_test_client(
        test_type=TEST_TYPE,
        app_cfg=app_cfg,
        verbose=False,
        log_level=logging.ERROR,
        use_endpoints=True,
    )
    assert env.endpoint_test_client is not None
    app = env.endpoint_test_client.app
    test_client = env.endpoint_test_client.test_client
    original_handle = app.handle

    def handle_with_block(cmd: Any) -> Any:
        if isinstance(cmd, blocked_command):
            entered_event.set()
            if not release_event.wait(timeout=WAIT_TIMEOUT):
                raise TimeoutError("Blocked command was not released")
        return original_handle(cmd)

    mocker.patch.object(app, "handle", side_effect=handle_with_block)

    def send_request(name: str, path: str) -> None:
        try:
            responses[name] = test_client.get(path)
        finally:
            if name == "other":
                other_finished.set()

    with test_client:
        blocked_thread = threading.Thread(
            target=send_request, args=("blocked", blocked_path)
        )
        other_thread = threading.Thread(target=send_request, args=("other", other_path))
        blocked_thread.start()
        try:
            assert entered_event.wait(timeout=WAIT_TIMEOUT)
            other_thread.start()
            assert other_finished.wait(timeout=WAIT_TIMEOUT / 2)
            assert responses["other"].status_code == 200
            assert blocked_thread.is_alive()
        finally:
            release_event.set()
            blocked_thread.join(timeout=WAIT_TIMEOUT)
            if other_thread.ident is not None:
                other_thread.join(timeout=WAIT_TIMEOUT)

    assert not blocked_thread.is_alive()
    assert not other_thread.is_alive()
    assert responses["blocked"].status_code == 200
