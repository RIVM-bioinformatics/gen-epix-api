# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later

import datetime
from typing import Any, Callable
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.common.domain import model
from gen_epix.common.util import generate_ulid
from gen_epix.fastapp import Command as ServiceCommand
from gen_epix.fastapp import CrudCommand as ServiceCrudCommand
from gen_epix.fastapp import UpdateAssociationCommand as ServiceUpdateAssociationCommand


class Command(ServiceCommand):
    id: UUID = Field(default_factory=generate_ulid, description="The ID of the command")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The created timestamp of the command",
    )
    user: model.User | None = None
    props: dict[str, Any] = {}

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime.datetime, _info: Any) -> str | None:
        return value.isoformat() if value else None

    @field_serializer("props")
    def serialize_props(self, value: dict, _info: Any) -> dict:
        return {x: y for x, y in value.items() if not isinstance(y, Callable)}  # type: ignore


class CrudCommand(ServiceCrudCommand, Command):
    user: model.User | None = None
    obj_ids: UUID | list[UUID] | None = None  # type: ignore


class UpdateAssociationCommand(ServiceUpdateAssociationCommand, Command):
    user: model.User | None = None
    obj_id1: UUID | list[UUID] | None = None
    obj_id2: UUID | list[UUID] | None = None
    association_objs: list[model.Model] | None = None
