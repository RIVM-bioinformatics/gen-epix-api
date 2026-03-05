"""
ReceiverApp CLI Module

This module provides a command-line interface for starting the ReceiverApp using Fire.
"""

import logging
import sys
from test.end_to_end.client_credential_flow.apps.receiver_app import ReceiverApp

import fire
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReceiverAppCLI:  # pylint: disable=too-few-public-methods
    """Command-line interface for ReceiverApp."""

    def run(
        self,
        port: int = 9001,
        oauth_discovery_url: str = "",
        ssl_keyfile: str | None = None,
        ssl_certfile: str | None = None,
    ) -> None:
        """
        Start the ReceiverApp server.

        Args:
            port: Port to run the server on (default: 9001)
            oauth_discovery_url: OAuth server discovery URL
        """
        if (ssl_keyfile is None) != (ssl_certfile is None):
            logger.error("Both ssl_keyfile and ssl_certfile must be provided, or none")
            sys.exit(1)
        if not oauth_discovery_url:
            logger.error("oauth_discovery_url is required")
            sys.exit(1)

        logger.info(f"Starting ReceiverApp on port {port}")
        logger.info(f"OAuth Discovery URL: {oauth_discovery_url}")

        # Create ReceiverApp instance
        receiver_app = ReceiverApp(port=port, oauth_discovery_url=oauth_discovery_url)

        # Run with uvicorn
        uvicorn.run(
            receiver_app.app,
            host="localhost",
            port=port,
            log_level="info",
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )


def main() -> None:
    """Main entry point for the CLI."""
    try:
        fire.Fire(ReceiverAppCLI)
    except KeyboardInterrupt:
        logger.info("ReceiverApp stopped by user")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"ReceiverApp failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
