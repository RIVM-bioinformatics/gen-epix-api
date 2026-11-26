# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later

"""Define commondb models for operational outages and package metadata.

System services persist outage windows for availability messaging and expose
non-persisted metadata about installed application packages.
"""

import datetime
import json
from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.enum import UploadJobStatus
from gen_epix.commondb.domain.model.base import Model, ModelNoId
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


class UploadJob(Model):
    """Represents an upload processed in the background and its outcome.

    An upload job is created when a client submits an upload asynchronously. The
    application returns the job immediately and processes the upload on a
    background worker in the same process; the client polls the job until its
    status is SUCCEEDED or FAILED. The job row is persisted so that any replica
    can answer status requests. A job whose worker stops sending heartbeats (e.g.
    because its pod was restarted) is reported as FAILED.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="upload_jobs",
        table_name="upload_job",
        persistable=True,
    )
    user_id: UUID = Field(description="The ID of the user that submitted the job.")
    job_type: str = Field(
        description="The name of the upload command processed by the job.",
        max_length=100,
    )
    status: UploadJobStatus = Field(description="The lifecycle state of the job.")
    submitted_at: datetime.datetime = Field(
        description="The date-time when the job was submitted."
    )
    started_at: datetime.datetime | None = Field(
        default=None, description="The date-time when processing of the job started."
    )
    finished_at: datetime.datetime | None = Field(
        default=None, description="The date-time when processing of the job finished."
    )
    heartbeat_at: datetime.datetime | None = Field(
        default=None,
        description="The date-time when the worker last reported that the job is alive.",
    )
    worker_id: str | None = Field(
        default=None,
        description="The ID of the worker process that owns the job.",
        max_length=255,
    )
    result_json: str | None = Field(
        default=None,
        description="The JSON-serialized upload result, when the job SUCCEEDED.",
    )
    error_status_code: int | None = Field(
        default=None,
        description="The HTTP status code the synchronous upload would have returned, when the job FAILED.",
    )
    error_detail: str | None = Field(
        default=None,
        description="A description of the error, when the job FAILED.",
        max_length=2000,
    )

    @property
    def is_finished(self) -> bool:
        """Return whether the job has reached a final status."""
        return self.status in {UploadJobStatus.SUCCEEDED, UploadJobStatus.FAILED}

    def get_result(self) -> Any:
        """Return the deserialized upload result, or None if there is none.

        Returns:
            The upload result as JSON-compatible data.
        """
        if self.result_json is None:
            return None
        return json.loads(self.result_json)


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


class DeleteAllOperationalDataResult(ModelNoId):
    """Represents the result of a delete all operational data operation."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="delete_all_operational_data_requests",
        persistable=False,
    )

    success: bool = Field(
        description="Indicates whether the deletion of all operational data was successful."
    )
    details: dict[str, str] = Field(
        default_factory=dict,
        description="Per model name, the number of deleted records as a string, or the error message when the deletion of that model failed.",
    )


class DeleteAllRefDataResult(ModelNoId):
    """Represents the result of a delete-all-reference-data operation."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="delete_all_ref_data_requests",
        persistable=False,
    )

    success: bool = Field(
        description="Indicates whether deletion of all reference data was successful."
    )
    details: dict[str, str] = Field(
        default_factory=dict,
        description="Detailed information about the result of the deletion operation.",
    )
