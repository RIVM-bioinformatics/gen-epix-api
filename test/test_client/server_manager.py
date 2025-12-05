import asyncio
import logging
import os
import signal
import subprocess
import threading
import time
from test.test_client.enum import ServerType, ServerTypeSet
from typing import Any

import httpx
import uvicorn


class ServerManager:
    """
    Server manager to handle startup of multiple servers including:
    - casedb
    - seqdb
    - omopdb
    - commondb
    - oauth server
    """

    DEFAULT_PORTS: dict[ServerType, int] = {
        ServerType.COMMONDB: 8010,
        ServerType.CASEDB: 8000,
        ServerType.SEQDB: 8001,
        ServerType.OMOPDB: 8002,
        ServerType.OAUTH: 9000,
        ServerType.OAUTH_RECEIVER: 9001,
    }

    DEFAULT_SCOPES = ["openid", "profile"]

    # Create logger
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.WARNING)

    # Create formatter for this specific logger
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create handler and apply formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    def __init__(
        self,
        service: ServerType,
        app: Any | None = None,
        host: str = "127.0.0.1",
        port: int | None = None,
        ssl_certfile: str | None = None,
        ssl_keyfile: str | None = None,
        oauth_discovery_url: str = "",
    ) -> None:
        if (ssl_certfile is None) != (ssl_keyfile is None):
            raise ValueError(
                "Both ssl_keyfile and ssl_certfile must be provided together"
            )
        self.service: ServerType = service
        self.app = app
        self.host = host
        self.port = port or self.DEFAULT_PORTS.get(service, 0)
        self.http_protocol = "https" if ssl_certfile and ssl_keyfile else "http"
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile

        self.server: uvicorn.Server | None = None
        self.thread: threading.Thread | None = None

        # oauth specific fields
        self.process: subprocess.Popen[str] | None = None
        self.base_url = f"{self.http_protocol}://localhost:{self.port}"
        self.oauth_discovery_url = oauth_discovery_url

        if self.service in ServerTypeSet.NON_AUTH.value:
            if app is None:
                raise ValueError("app must be provided for non-OAuth servers")

    @staticmethod
    def _create_process_kwargs() -> dict[str, Any]:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        popen_kwargs: dict[str, Any] = {
            "cwd": os.getcwd(),
            "env": env,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "universal_newlines": True,
            "bufsize": 1,
        }

        if os.name == "posix":
            popen_kwargs["preexec_fn"] = getattr(os, "setsid", None)
        elif os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        return popen_kwargs

    def _start_log_monitor(self) -> None:

        def log_output() -> None:
            if not self.process or not self.process.stdout:
                return

            for line in self.process.stdout:
                line_stripped = line.strip()
                if line_stripped:
                    print(f"[{self.service.value}] {line_stripped}")

        if self.process:
            log_thread = threading.Thread(
                target=log_output, daemon=True, name=f"{self.service.value.lower()}-log"
            )
            log_thread.start()

    def start_oauth_server(self) -> bool:
        if self.process:
            self.stop()

        if self.service == ServerType.OAUTH:
            cmd: list[str] = [
                "python",
                "-m",
                "uvicorn",
                "test.test_client.oauth.server:app",
                "--host",
                "localhost",
                "--port",
                str(self.port),
                "--log-level",
                "info",
            ]
            if self.ssl_keyfile:
                cmd.extend(
                    [
                        "--ssl-keyfile",
                        self.ssl_keyfile,
                        "--ssl-certfile",
                        self.ssl_certfile,
                    ]
                )
        elif self.service == ServerType.OAUTH_RECEIVER:
            if self.oauth_discovery_url == "":
                raise ValueError(
                    "oauth_discovery_url must be provided for receiver app"
                )
            cmd = [
                "python",
                "-m",
                "test.end_to_end.client_credential_flow.apps.receiver_app_cli",
                "run",
                f"--port={self.port}",
                f"--oauth_discovery_url={self.oauth_discovery_url}",
            ]
        else:
            raise ValueError("Invalid service type for OAuth server")

        popen_kwargs = self._create_process_kwargs()

        try:
            self.process = subprocess.Popen(cmd, **popen_kwargs)
            self._start_log_monitor()
            return self._wait_for_server()
        except Exception as e:
            self.LOGGER.error(f"Failed to start OAuth server: {e}")
            return False

    def add_client(
        self,
        client_id: str,
        client_secret: str,
        audience: str | None = None,
        scopes: list[str] | None = None,
    ) -> bool:
        if self.service not in ServerTypeSet.AUTH.value:
            raise RuntimeError("add_client is only supported for OAuth server")
        scopes = scopes or self.DEFAULT_SCOPES
        client_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": f"{client_id} M2M Client",
            "scopes": scopes,
            "grant_types": ["client_credentials"],
            "redirect_uris": [],
            "audience": audience,
        }
        try:
            with httpx.Client(timeout=10.0, verify=self.ssl_certfile) as client:
                response = client.post(
                    f"{self.base_url}/admin/clients", json=client_data
                )
                if response.status_code == 201:
                    self.LOGGER.info(
                        f"Successfully added M2M client {client_id} with audience {audience}"
                    )
                    return True
                elif response.status_code == 409:
                    # Client already exists
                    self.LOGGER.info(f"M2M client {client_id} already exists")
                    return True
                else:
                    self.LOGGER.error(
                        f"Failed to add M2M client: {response.status_code} - {response.text}"
                    )
                    return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.LOGGER.error(f"Error adding M2M client: {e}")
            return False

    def get_discovery_url(self) -> str:
        if self.service in ServerTypeSet.AUTH.value:
            return f"{self.base_url}/.well-known/openid-configuration"
        else:
            raise RuntimeError("get_discovery_url is only supported for OAuth server")

    def delete_client(self, client_id: str) -> bool:
        if self.service not in ServerTypeSet.AUTH.value:
            raise RuntimeError("delete_client is only supported for OAuth server")
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.delete(f"{self.base_url}/admin/clients/{client_id}")
                if response.status_code == 204:
                    self.LOGGER.info(f"Successfully deleted client {client_id}")
                    return True
                elif response.status_code == 404:
                    self.LOGGER.info(f"Client {client_id} not found (already deleted)")
                    return True
                else:
                    self.LOGGER.error(
                        f"Failed to delete client: {response.status_code} - {response.text}"
                    )
                    return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.LOGGER.error(f"Error deleting client: {e}")
            return False

    def start_uvicorn_server(self) -> bool:
        try:
            self.LOGGER.info("Starting %s server on %s", self.service, self.host)
            config: uvicorn.Config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False,
                ssl_certfile=self.ssl_certfile,
                ssl_keyfile=self.ssl_keyfile,
            )
            self.server = uvicorn.Server(config=config)

            def run_server() -> None:
                if self.server:
                    asyncio.run(self.server.serve())

            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()

            # Wait for the server to start
            is_ready = self._wait_for_server()
            if is_ready:
                self.LOGGER.info("%s server started successfully", self.service)
            return is_ready
        except Exception as e:
            self.LOGGER.error(f"Failed to start {self.service} server: {e}")
            return False

    def start(self) -> bool:
        if self.service in ServerTypeSet.AUTH.value:
            return self.start_oauth_server()
        else:
            return self.start_uvicorn_server()

    def _wait_for_server(self, timeout: int = 10) -> bool:
        start_time = time.time()
        if self.service in ServerTypeSet.AUTH.value:
            health_url = "/health"
        else:
            health_url = "/v1/health"

        while time.time() - start_time < timeout:
            if self.process:
                if self.process.poll() is not None:
                    self.LOGGER.error("Server process terminated unexpectedly")
                    return False
            try:
                with httpx.Client(timeout=5.0, verify=self.ssl_certfile) as client:
                    response = client.get(
                        f"{self.http_protocol}://{self.host}:{self.port}{health_url}"
                    )
                    if response.status_code == 200:
                        return True
            except Exception as e:
                self.LOGGER.debug("Error while checking server health: %s", e)
            time.sleep(0.1)
        return False

    def stop_uvicorn_server(self) -> None:
        if self.server:
            self.server.should_exit = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

    def stop_oauth_server(self) -> None:
        if not self.process:
            return

        try:
            if os.name == "posix":
                killpg = getattr(os, "killpg", None)
                getpgid = getattr(os, "getpgid", None)
                if (
                    killpg
                    and getpgid
                    and self.process.pid
                    and callable(killpg)
                    and callable(getpgid)
                ):
                    killpg(
                        getpgid(self.process.pid), signal.SIGTERM
                    )  # pylint: disable=not-callable
            elif os.name == "nt":
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            self.process.wait(timeout=10)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            if os.name == "posix":
                try:
                    killpg = getattr(os, "killpg", None)
                    getpgid = getattr(os, "getpgid", None)
                    sigkill = getattr(signal, "SIGKILL", None)
                    if (  # pylint: disable=too-many-boolean-expressions
                        killpg
                        and getpgid
                        and sigkill
                        and self.process.pid
                        and callable(killpg)
                        and callable(getpgid)
                    ):
                        killpg(
                            getpgid(self.process.pid), sigkill
                        )  # pylint: disable=not-callable
                except ProcessLookupError:
                    # Process group already does not exist; safe to ignore during cleanup
                    pass
            elif os.name == "nt":
                self.process.kill()
        finally:
            if self.process:
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()
                self.process = None

        self.LOGGER.info(f"{self.service.value} stopped")

    def stop(self) -> None:
        if self.service in ServerTypeSet.AUTH.value:
            self.stop_oauth_server()
        else:
            self.stop_uvicorn_server()

    def __enter__(self) -> "ServerManager":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
