"""
OAuth Server Manager Module

This module manages the OAuth server process for testing OAuth Client Credentials flow.
"""

import logging
import subprocess
from test.test_client.oauth.base_process_manager import BaseProcessManager

import httpx

# Configure logging
logger = logging.getLogger(__name__)


class OAuthServerManager(BaseProcessManager):
    """Manages the OAuth server process for testing."""

    DEFAULT_SCOPES = ["openid", "profile"]

    def __init__(
        self,
        port: int = 8000,
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
    ):
        super().__init__(
            port, "OAuth Server", ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile
        )

    def start(self) -> bool:
        """Start the OAuth server."""
        if self.process:
            self.stop()

        # Start OAuth server process
        cmd = [
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
                ["--ssl-keyfile", self.ssl_keyfile, "--ssl-certfile", self.ssl_certfile]
            )

        popen_kwargs = self._create_process_kwargs()

        try:
            # Use context manager for subprocess to ensure proper cleanup
            self.process = subprocess.Popen(cmd, **popen_kwargs)  # type: ignore[misc] # pylint: disable=consider-using-with
            self._start_log_monitor()
            return self._wait_for_server()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to start OAuth server: {e}")
            return False

    def add_client(
        self,
        client_id: str,
        client_secret: str,
        audience: str | None = None,
        scopes: list[str] | None = None,
    ) -> bool:
        """Add a machine-to-machine client to the server."""
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
                    logger.info(
                        f"Successfully added M2M client {client_id} with audience {audience}"
                    )
                    return True
                elif response.status_code == 409:
                    # Client already exists
                    logger.info(f"M2M client {client_id} already exists")
                    return True
                else:
                    logger.error(
                        f"Failed to add M2M client: {response.status_code} - {response.text}"
                    )
                    return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Error adding M2M client: {e}")
            return False

    def get_discovery_url(self) -> str:
        """Get the OpenID Connect discovery URL."""
        return f"{self.base_url}/.well-known/openid-configuration"

    def delete_client(self, client_id: str) -> bool:
        """Delete a client from the server."""
        import httpx

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.delete(f"{self.base_url}/admin/clients/{client_id}")
                if response.status_code == 204:
                    logger.info(f"Successfully deleted client {client_id}")
                    return True
                elif response.status_code == 404:
                    logger.info(f"Client {client_id} not found (already deleted)")
                    return True
                else:
                    logger.error(
                        f"Failed to delete client: {response.status_code} - {response.text}"
                    )
                    return False
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Error deleting client: {e}")
            return False

    def __enter__(self) -> "OAuthServerManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.stop()
