"""Service for forwarding commands to remote applications."""

from typing import Any

from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.service import BaseService


class BaseRemoteService(BaseService):
    """Provide the base remote service framework abstraction."""

    def __init__(self, app: App, remote_app: App, use_endpoints: bool = True) -> None:
        """Initialize the instance."""
        super().__init__(app)
        self._remote_app = remote_app
        self._use_endpoints = use_endpoints

    @property
    def remote_app(self) -> App:
        """Perform the remote app operation."""
        return self._remote_app

    @property
    def use_endpoints(self) -> bool:
        """Perform the use endpoints operation."""
        return self._use_endpoints

    @use_endpoints.setter
    def use_endpoints(self, value: bool) -> None:
        """Perform the use endpoints operation."""
        self._use_endpoints = value

    def handle(
        self,
        cmd: Command,
    ) -> Any:
        """Perform the handle operation."""
        if self.use_endpoints:
            raise NotImplementedError()
        else:
            return self.remote_app.handle(cmd)
