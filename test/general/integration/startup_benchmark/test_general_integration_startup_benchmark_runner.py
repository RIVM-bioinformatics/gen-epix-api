import dataclasses
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.startup_benchmark.models import Application, Options
from scripts.startup_benchmark.runner import cleanup, run_once

pytestmark = pytest.mark.integration
CHILD = Path(__file__).with_name("http_child.py")


@pytest.fixture
def options(monkeypatch):
    monkeypatch.setattr(
        "scripts.startup_benchmark.runner.tls_context", lambda options: None
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return Options(
        Application("test", port, "TEST"),
        "NONE",
        "DICT_EMPTY",
        readiness_timeout=2,
        request_timeout=0.1,
        poll_interval=0.02,
        settle_seconds=0,
    )


@pytest.mark.parametrize(
    "behavior,status",
    [
        ("normal", "success"),
        ("delay", "success"),
        ("retry", "success"),
        ("wrong", "identity_failure"),
        ("missing", "identity_failure"),
        ("exit", "premature_exit"),
        ("non200", "timeout"),
        ("redirect", "timeout"),
        ("slow", "timeout"),
    ],
)
def test_readiness_and_cleanup(options, tmp_path, behavior, status):
    if status == "timeout":
        options = dataclasses.replace(options, readiness_timeout=0.4)
    record = run_once(
        options,
        tmp_path,
        1,
        "measured",
        dict(os.environ),
        [sys.executable, str(CHILD), str(options.application.port), behavior],
    )
    assert record.status == status
    assert record.cleanup == "ok"
    assert (record.seconds is not None) == (status == "success")
    assert Path(record.stderr).exists()
    assert record.exit_code is not None


def test_occupied_port_is_not_stopped(options, tmp_path):
    with socket.socket() as sock:
        sock.bind(("0.0.0.0", options.application.port))
        record = run_once(options, tmp_path, 1, "measured", dict(os.environ))
        assert record.status == "occupied_port"
        assert record.pid is None
        assert sock.getsockname()[1] == options.application.port


def test_launch_failure(options, tmp_path):
    record = run_once(
        options, tmp_path, 1, "measured", dict(os.environ), ["/no/such/executable"]
    )
    assert record.status == "launch_failure"
    assert record.cleanup == "not_needed"


def test_refused_connections(options, tmp_path):
    options = dataclasses.replace(options, readiness_timeout=0.1)
    record = run_once(
        options,
        tmp_path,
        1,
        "measured",
        dict(os.environ),
        [sys.executable, "-c", "import time; time.sleep(10)"],
    )
    assert record.status == "timeout"
    assert record.cleanup == "ok"


def test_interruption_cleans_process(options, tmp_path, monkeypatch):
    from scripts.startup_benchmark import runner

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(runner.http.client, "HTTPConnection", interrupt)
    record = run_once(
        options,
        tmp_path,
        1,
        "measured",
        dict(os.environ),
        [sys.executable, "-c", "import time; time.sleep(10)"],
    )
    assert record.status == "interrupted"
    assert record.cleanup == "ok"


def test_descendant_ignoring_sigterm_is_killed(tmp_path):
    ready = tmp_path / "ready"
    script = 'import signal,time,sys; from pathlib import Path; signal.signal(signal.SIGTERM, signal.SIG_IGN); Path(sys.argv[1]).write_text("ready"); time.sleep(120)'
    parent_script = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",sys.argv[1],sys.argv[2]]); time.sleep(120)'
    process = subprocess.Popen(
        [sys.executable, "-c", parent_script, script, str(ready)],
        start_new_session=True,
    )
    import time

    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists()
        assert cleanup(process, grace=0.1)
    finally:
        cleanup(process, grace=0.1)


@pytest.mark.parametrize("app", ["casedb", "seqdb", "omopdb"])
def test_real_header_configuration_and_debug(app, monkeypatch):
    from fastapi import FastAPI
    from starlette.testclient import TestClient

    from gen_epix.commondb.domain.util import get_app_cfg_class, set_env_variables
    from gen_epix.fastapp.middleware.update_response_header import (
        UpdateResponseHeaderMiddleware,
    )
    from scripts.startup_benchmark.models import APPLICATIONS
    from scripts.startup_benchmark.runner import child_environment

    option = Options(APPLICATIONS[app], "NONE", "DICT_EMPTY")
    key = f"{app.upper()}_API__HTTP_HEADER__GENERAL"
    monkeypatch.setenv(key, '@json {"X-Existing": "preserved"}')
    env = child_environment(dict(os.environ), option, "verified")
    monkeypatch.setenv(key, env[key])
    # Isolate set_env_variables side effects between app contract tests.
    for prefix in (app.upper(), "SEQDB"):
        for suffix in ("SETTINGS_FILES", "LOG_CONFIG_FILE"):
            monkeypatch.setenv(prefix + "_" + suffix, "")
    set_env_variables(app, "NONE", "DICT_EMPTY")
    cfg = get_app_cfg_class(
        __import__("gen_epix.commondb.domain.enum", fromlist=["AppType"]).AppType[
            app.upper()
        ]
    )()
    assert cfg.cfg["app"]["debug"] is False
    api = FastAPI()
    api.add_middleware(
        UpdateResponseHeaderMiddleware,
        general_headers=cfg.cfg["api"]["http_header"]["general"],
    )

    @api.get("/v1/health")
    def health():
        return {}

    response = TestClient(api).get("/v1/health")
    assert response.headers["X-Existing"] == "preserved"
    assert response.headers["X-Startup-Benchmark-Instance"] == "verified"


def test_port_race_cannot_accept_competing_instance(options, tmp_path, monkeypatch):
    import time

    from scripts.startup_benchmark import runner

    env = runner.child_environment(dict(os.environ), options, "stale-instance")
    competing = subprocess.Popen(
        [sys.executable, str(CHILD), str(options.application.port), "normal"],
        env=env,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(
                    ("127.0.0.1", options.application.port), timeout=0.1
                ):
                    break
            except OSError:
                time.sleep(0.01)
        else:
            pytest.fail("Controlled competing server did not start")
        # Simulate a competitor binding just after the pre-launch availability probe.
        original = runner.port_available
        probes = []

        def raced(port):
            probes.append(port)
            return True if len(probes) == 1 else original(port)

        monkeypatch.setattr(runner, "port_available", raced)
        record = run_once(
            options,
            tmp_path,
            1,
            "measured",
            dict(os.environ),
            [sys.executable, "-c", "import time; time.sleep(10)"],
        )
        assert record.status == "identity_failure"
        assert record.seconds is None
        assert competing.poll() is None
    finally:
        cleanup(competing, grace=0.1)
