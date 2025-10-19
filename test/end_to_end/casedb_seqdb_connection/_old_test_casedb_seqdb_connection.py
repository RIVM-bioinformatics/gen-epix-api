"""Test connection between casedb, seqdb and/or omopdb"""

import os
import signal
import ssl
import subprocess
import threading
import time
from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
from typing import Generator

import httpx
import pytest

from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.util import set_env_variables

set_envvar()


class ServiceManager:
    """Manages casedb, seqdb and possibly omopdb services for testing purposes."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.processes: dict[str, subprocess.Popen] = {}
        self.ports = {
            "casedb": 8000,
            "seqdb": 8001,
            # "omopdb": 8002, # uncomment if needed
        }
        self.base_urls = {
            service: f"https://localhost:{port}" for service, port in self.ports.items()
        }

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context that trusts the local certificate."""
        ssl_context = ssl.create_default_context()
        cert_file = os.path.join(self.project_root, "cert", "cert.pem")
        if os.path.exists(cert_file):
            ssl_context.load_verify_locations(cert_file)
        return ssl_context

    def start_service(
        self,
        service_name: str,
        idp_config: DevIdpConfig = DevIdpConfig.MOCK,
        dev_repository_config: DevRepositoryConfig = DevRepositoryConfig.DICT_EMPTY,
    ) -> bool:
        """Start a service (casedb, seqdb, omopdb) in a subprocess."""

        if service_name not in self.ports:
            raise ValueError(f"Unknown service: {service_name}")

        if service_name in self.processes:
            print(f"{service_name} is already running. Stopping it first.")
            self.stop_service(service_name)

        cmd = [
            "python",
            "run.py",
            "api",
            service_name,
            idp_config.value,
            dev_repository_config.value,
        ]

        print(f"Starting {service_name} with command: {' '.join(cmd)}")

        set_env_variables(
            AppType[service_name.upper()],
            DevIdpConfig.MOCK,
            DevRepositoryConfig.DICT_EMPTY,
        )
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": self.project_root,
            }
        )

        popen_kwargs = {
            "cwd": self.project_root,
            "env": env,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "universal_newlines": True,
            "bufsize": 1,
        }
        if os.name == "posix":
            popen_kwargs["preexec_fn"] = (
                os.setsid
            )  # To allow killing the whole process group
        elif os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            cmd,
            **popen_kwargs,
        )

        self.processes[service_name] = process
        self._start_log_monitor(service_name, process)

        return self._wait_for_service(service_name)

    def _start_log_monitor(self, service_name: str, process: subprocess.Popen) -> None:
        """Monitor service logs and detect startup completion."""

        def log_output() -> None:
            startup_indicators = [
                "Application startup complete",
                "Uvicorn running on",
                "Started server process",
            ]

            for line in process.stdout:
                line_stripped = line.strip()
                if line_stripped:
                    print(f"[{service_name}] {line_stripped}")

                    # Signal when service is truly ready
                    if any(
                        indicator in line_stripped for indicator in startup_indicators
                    ):
                        print(f"[{service_name}] Startup indicator detected")

        log_thread = threading.Thread(
            target=log_output, daemon=True, name=f"{service_name}-log"
        )
        log_thread.start()

    def stop_service(self, service_name: str) -> None:
        """Stop a running service."""

        if service_name not in self.processes:
            return

        process = self.processes[service_name]

        try:
            if os.name == "posix":
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            elif os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            process.wait(timeout=10)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            if os.name == "posix":
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already terminated
            elif os.name == "nt":
                process.kill()
        finally:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            if service_name in self.processes:
                del self.processes[service_name]

        print(f"{service_name} stopped.")

    # TODO: reset timeout to 60 seconds
    def _wait_for_service(
        self, service_name: str, timeout: int = 60_000
    ) -> bool:  # I timed startup to ~25 sec
        """Wait for a service to start by checking its health endpoint."""

        if service_name not in self.processes:
            raise ValueError(f"Unknown service: {service_name}")

        url = f"{self.base_urls[service_name]}/v1/identity_providers"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.processes[service_name].poll() is not None:
                print(f"{service_name} process has terminated")
                return False

            try:
                # Use SSL context that trusts our local certificate or disable verification for testing
                with httpx.Client(verify=False) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"{service_name} is up and running.")
                        return True
            except httpx.ConnectError as e:
                print(f"Connection error for {service_name}: {e}")
                pass  # Continue trying instead of raising
            time.sleep(1)

        print(f"Timeout waiting for {service_name} to start.")
        return False

    def stop_all_services(self) -> None:
        """Stop all running services."""
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        print("All services stopped.")

    def start_services(self, services: list[str], **kwargs: str) -> bool:
        """Start multiple services."""
        for service in services:
            if not self.start_service(service, **kwargs):
                return False
        return True

    def get_base_url(self, service_name: str) -> str:
        """Get the base URL for a service."""
        return self.base_urls.get(service_name, "")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_all_services()


@pytest.fixture(scope="session")
def service_manager_fixture() -> Generator[ServiceManager, None, None]:
    with ServiceManager(project_root=os.getcwd()) as manager:
        yield manager


@pytest.fixture(scope="session")
def start_casedb_and_seqdb(
    service_manager_fixture: ServiceManager,
) -> Generator[dict[str, str], None, None]:
    """Start CaseDB and SeqDB services."""
    is_succes = service_manager_fixture.start_services(["seqdb", "casedb"])

    if not is_succes:
        service_manager_fixture.stop_all_services()
        raise RuntimeError("Failed to start CaseDB and SeqDB services.")

    yield {
        "seqdb_url": service_manager_fixture.get_base_url("seqdb"),
        "casedb_url": service_manager_fixture.get_base_url("casedb"),
    }


@pytest.fixture(scope="function")
def test_client_fixture(
    start_casedb_and_seqdb: dict[str, str],
) -> Generator[tuple[httpx.Client, dict[str, str]], None, None]:
    """Provide a httpx client for testing."""
    with httpx.Client(verify=False) as client:  # Disable SSL verification for testing
        yield client, start_casedb_and_seqdb


def test_casedb_calls_seqdb_health(
    test_client_fixture: tuple[httpx.Client, dict[str, str]],
) -> None:
    client, urls = test_client_fixture
    seqdb_url = urls["seqdb_url"]

    response = client.get(f"{seqdb_url}/v1/health")
    assert response.status_code == 200
    assert response.json().get("status") == "HEALTHY"
