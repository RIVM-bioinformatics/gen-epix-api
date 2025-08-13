# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import datetime
from typing import ClassVar

from pydantic import Field

from gen_epix.common.domain import enum
from gen_epix.common.domain.model.base import Model
from gen_epix.fastapp import Entity

_SERVICE_TYPE = enum.ServiceType.SYSTEM
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class Outage(Model):
    """
    Represents a system outage.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="outages",
        table_name="outage",
        persistable=True,
        **_ENTITY_KWARGS,
    )
    description: str | None = Field(
        default=None, description="Description of the system outage."
    )
    active_from: datetime.datetime | None = Field(
        default=None, description="The date-time when the system outage starts."
    )
    active_to: datetime.datetime | None = Field(
        default=None, description="The date-time when the system outage ends."
    )
    visible_from: datetime.datetime | None = Field(
        default=None, description="The date-time when the system outage is announced."
    )
    visible_to: datetime.datetime | None = Field(
        default=None,
        description="The date-time when the system outage is no longer announced.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the system outage is currently active, this overrides active_from and active_to.",
    )
    is_visible: bool | None = Field(
        default=None,
        description="Whether the system outage is currently visible, this overrides visible_from and visible_to.",
    )
