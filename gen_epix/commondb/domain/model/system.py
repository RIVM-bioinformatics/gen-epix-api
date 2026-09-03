# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later

"""Define commondb models for operational outages and package metadata.

System services persist outage windows for availability messaging and expose
non-persisted metadata about installed application packages.
"""

import datetime
from typing import ClassVar

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity


class Outage(Model):
    """Represents an active or scheduled system outage and its visibility window."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="outages",
        table_name="outage",
        persistable=True,
    )
    description: str | None = Field(
        default=None, description="Description of the system outage.", max_length=1000
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


class PackageMetadata(Model):
    """Represents descriptive metadata for a package without persisting it."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="package_metadatas",
        persistable=False,
    )

    name: str = Field(description="Name of the package.")
    version: str = Field(description="Version of the package.")
    license: str | None = Field(
        default=None, description="License information for the package."
    )
    homepage: str | None = Field(
        default=None, description="Homepage URL of the package."
    )
