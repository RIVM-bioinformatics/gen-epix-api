"""Service for forwarding commands to remote applications."""

from typing import Any

from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.service import BaseService


class BaseRemoteService(BaseService):
    """Encapsulates the base service that forwards commands to a remote application
    through a client for that application.
    """

    def __init__(self, app: App, client: App, use_endpoints: bool = True) -> None:
        """Initialize a BaseRemoteService instance."""
        super().__init__(app)
        self._client = client
        self._use_endpoints = use_endpoints

    @property
    def client(self) -> App:
        """Remote app."""
        return self._client

    @property
    def use_endpoints(self) -> bool:
        """Use endpoints."""
        return self._use_endpoints

    @use_endpoints.setter
    def use_endpoints(self, value: bool) -> None:
        """Use endpoints."""
        self._use_endpoints = value

    def handle(
        self,
        cmd: Command,
    ) -> Any:
        """Handle the requested value."""
        if self.use_endpoints:
            raise NotImplementedError()
        else:
            return self.client.handle(cmd)
