from typing import Any

from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.model import Command
from gen_epix.omopdb.domain import DOMAIN


class OmopdbRemoteApp(CommondbRemoteApp):

    ROUTE_MAP: dict[type[Command], str] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)

        # Register routes and handlers
