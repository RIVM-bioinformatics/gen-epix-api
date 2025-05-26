# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later

import datetime
from typing import Any, Callable, ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.fastapp import Command as ServiceCommand
from gen_epix.fastapp import CrudCommand as ServiceCrudCommand
from gen_epix.omopdb.domain import model
from util.util import generate_ulid


class Command(ServiceCommand):
    id: UUID = Field(default_factory=generate_ulid, description="The ID of the command")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The created timestamp of the command",
    )
    user: model.User | None = None
    props: dict[str, Any] = {}

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime.datetime, _info):
        return value.isoformat() if value else None

    @field_serializer("props")
    def serialize_props(self, value: dict, _info):
        return {x: y for x, y in value.items() if not isinstance(y, Callable)}  # type: ignore


class CrudCommand(ServiceCrudCommand, Command):
    MODEL_CLASS: ClassVar = Command
    user: model.User | None = None
    props: dict[str, Any] = {}
    obj_ids: UUID | list[UUID] | None = None  # type: ignore
