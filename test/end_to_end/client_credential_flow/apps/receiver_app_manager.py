"""
ReceiverApp Manager Module

This module manages the ReceiverApp server process for testing.
"""

import logging
import subprocess
from test.test_client.oauth.base_process_manager import BaseProcessManager

# Configure logging
logger = logging.getLogger(__name__)


class ReceiverAppManager(BaseProcessManager):
    """Manages the ReceiverApp server process."""

    def __init__(self, port: int = 8001, oauth_discovery_url: str = ""):
        super().__init__(port, "ReceiverApp")
        self.oauth_discovery_url = oauth_discovery_url

    def start(self) -> bool:
        """Start the ReceiverApp server."""
        if self.process:
            self.stop()

        try:
            cmd = [
                "python",
                "-m",
                "test.end_to_end.client_credential_flow.apps.receiver_app_cli",
                "run",
                f"--port={self.port}",
                f"--oauth_discovery_url={self.oauth_discovery_url}",
            ]

            popen_kwargs = self._create_process_kwargs()

            self.process = subprocess.Popen(cmd, **popen_kwargs)  # type: ignore[misc] # pylint: disable=consider-using-with
            self._start_log_monitor()

            return self._wait_for_server()

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to start ReceiverApp: {e}")
            return False

    def __enter__(self) -> "ReceiverAppManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.stop()
