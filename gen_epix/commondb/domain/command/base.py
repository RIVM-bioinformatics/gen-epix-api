# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later

import datetime
from collections.abc import Callable
from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.commondb import enum
from gen_epix.commondb.domain import model
from gen_epix.fastapp import Command as ServiceCommand
from gen_epix.fastapp import CrudCommand as ServiceCrudCommand
from gen_epix.fastapp import UpdateAssociationCommand as ServiceUpdateAssociationCommand
from gen_epix.util import generate_ulid


class Command(ServiceCommand):
    id: UUID = Field(default_factory=generate_ulid, description="The ID of the command")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The created timestamp of the command",
    )
    user: model.User | None = None
    props: dict[str, Any] = {}

    @field_serializer("created_at", mode="plain")
    def _serialize_created_at(self, value: datetime.datetime) -> str | None:
        return value.isoformat() if value else None

    @field_serializer("props", mode="plain")
    def _serialize_props(self, value: dict[str, Any]) -> dict[str, Any]:
        return {x: y for x, y in value.items() if not isinstance(y, Callable)}


class CrudCommand(ServiceCrudCommand, Command):
    user: model.User | None = None
    obj_ids: UUID | list[UUID] | None = None  # type: ignore


class UpdateAssociationCommand(ServiceUpdateAssociationCommand, Command):
    user: model.User | None = None
    obj_id1: UUID | list[UUID] | None = None
    obj_id2: UUID | list[UUID] | None = None
    association_objs: list[model.Model] | None = None


class UploadBatchCommandMixin:
    """Mixin class for BatchForUpload classes providing common functionality."""

    # Must be set in child class
    # The BaseBatchForUpload child class that this command uploads
    BATCH_FOR_UPLOAD_CLASS: ClassVar[type[model.BaseBatchForUpload]] = None  # type: ignore[assignment]

    # Must be set in child class
    # The name of the field containing the BatchForUpload object
    BATCH_FOR_UPLOAD_FIELD_NAME: ClassVar[str] = None  # type: ignore[assignment]

    # Must be set in child class
    # The BaseBatchUploadResult child class that will contain the results of the upload
    BATCH_UPLOAD_RESULT_CLASS: ClassVar[type[model.BaseBatchUploadResult]] = None  # type: ignore[assignment]

    verify_only: bool = Field(
        default=False,
        description="If true, the upload is only verified but not actually performed.",
    )
    on_exists: enum.OnExistsUploadAction = Field(
        default=enum.OnExistsUploadAction.ERROR,
        description="Action to take if one of the entities in the batch already exists upon upload.",
    )

    def get_batch_for_upload(self) -> model.BaseBatchForUpload:
        """Get the batch for upload from the command."""
        batch_for_upload: model.BaseBatchForUpload = getattr(
            self, self.BATCH_FOR_UPLOAD_FIELD_NAME
        )
        return batch_for_upload
