import asyncio
import logging
import threading
import time
from typing import Any

import httpx
import uvicorn


class SeqdbServerManager:
    """Manages the SeqDB FastAPI server for testing."""

    def __init__(
        self,
        app: Any,
        host: str = "127.0.0.1",
        port: int = 8001,
        ssl_certfile: str | None = None,
        ssl_keyfile: str | None = None,
    ) -> None:
        if (ssl_certfile is None) != (ssl_keyfile is None):
            raise ValueError(
                "Both ssl_keyfile and ssl_certfile must be provided together"
            )
        self.app = app
        self.host = host
        self.port = port
        self.http_protocol = "https" if ssl_certfile and ssl_keyfile else "http"
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        self.server: uvicorn.Server | None = None
        self.thread: threading.Thread | None = None

    def start(self) -> bool:
        """Start the SeqDB server in a separate thread."""
        try:
            logging.info(f"Starting SeqDB server on {self.host}:{self.port}")
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="error",  # Reduce noise in tests
                access_log=False,
                ssl_certfile=self.ssl_certfile,
                ssl_keyfile=self.ssl_keyfile,
            )
            self.server = uvicorn.Server(config)

            def run_server() -> None:
                if self.server:
                    asyncio.run(self.server.serve())

            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()

            # Wait for server to start
            is_ready = self._wait_for_server()
            logging.info(f"SeqDB server ready: {is_ready}")
            return is_ready
        except Exception as e:
            logging.error(
                f"Failed to start SeqDB server on {self.host}:{self.port}: {e}"
            )
            return False

    def _wait_for_server(self, timeout: int = 10) -> bool:
        """Wait for the SeqDB server to become available."""
        start_time = time.time()
        health_path = "/v1/health"

        while time.time() - start_time < timeout:
            try:
                with httpx.Client(timeout=1.0, verify=self.ssl_certfile) as client:
                    response = client.get(
                        f"{self.http_protocol}://{self.host}:{self.port}{health_path}"
                    )
                    if response.status_code == 200:
                        return True
            except Exception:
                pass
            time.sleep(0.1)
        return False

    def stop(self) -> None:
        """Stop the SeqDB server."""
        if self.server:
            self.server.should_exit = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

    def __enter__(self) -> "SeqdbServerManager":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
