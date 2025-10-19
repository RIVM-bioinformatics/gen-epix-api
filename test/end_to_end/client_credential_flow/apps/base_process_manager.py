"""
Base Process Manager Module

This module contains shared functionality for managing server processes.
"""

import logging
import os
import signal
import subprocess
import threading
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BaseProcessManager:  # pylint: disable=too-few-public-methods
    """Base class for managing server processes."""

    def __init__(self, port: int, service_name: str):
        self.port = port
        self.service_name = service_name
        self.process: subprocess.Popen[str] | None = None
        self.base_url = f"http://localhost:{port}"

    def _create_process_kwargs(self) -> dict[str, Any]:
        """Create common subprocess kwargs."""
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
        """Monitor server logs."""

        def log_output() -> None:
            if not self.process or not self.process.stdout:
                return

            for line in self.process.stdout:
                line_stripped = line.strip()
                if line_stripped:
                    print(f"[{self.service_name}] {line_stripped}")

        if self.process:
            log_thread = threading.Thread(
                target=log_output, daemon=True, name=f"{self.service_name.lower()}-log"
            )
            log_thread.start()

    def _wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for server to be ready."""
        start_time = time.time()
        health_url = f"{self.base_url}/health"

        while time.time() - start_time < timeout:
            if self.process and self.process.poll() is not None:
                logger.error(f"{self.service_name} process terminated")
                return False

            try:
                with httpx.Client() as client:
                    response = client.get(health_url, timeout=5.0)
                    if response.status_code == 200:
                        logger.info(f"{self.service_name} is ready")
                        return True
            except httpx.ConnectError:
                pass

            time.sleep(1)

        logger.error(f"Timeout waiting for {self.service_name}")
        return False

    def stop(self) -> None:  # pylint: disable=too-many-branches
        """Stop the server."""
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

        logger.info(f"{self.service_name} stopped")
