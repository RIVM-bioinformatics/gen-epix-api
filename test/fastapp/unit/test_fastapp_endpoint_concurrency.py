"""Verify that synchronous command handling does not block other API requests."""

import logging
import threading
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from typing import Any

from gen_epix.commondb.domain import enum
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

    app_cfg = APP_CFGS[f"{TEST_TYPE}__{DevRepositoryConfig.DICT_EMPTY.value}"]
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
