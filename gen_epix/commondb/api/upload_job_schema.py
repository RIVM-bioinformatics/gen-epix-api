"""Define the API response model for upload jobs.

Upload endpoints that process an upload in the background return an upload job
immediately (HTTP 202). The client polls the job until its status is SUCCEEDED,
when ``result`` holds what the synchronous endpoint would have returned, or
FAILED, when ``error_status_code`` and ``error_detail`` describe the error the
synchronous endpoint would have raised.
"""

import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix.commondb.domain import enum, model

ResultT = TypeVar("ResultT", bound=BaseModel)


class UploadJobResponse(BaseModel, Generic[ResultT]):
    """Represents the status of an upload job and, once it succeeded, its result."""

    id: UUID = Field(description="The ID of the upload job.")
    status: enum.UploadJobStatus = Field(description="The lifecycle state of the job.")
    submitted_at: datetime.datetime = Field(
        description="The date-time when the job was submitted."
    )
    started_at: datetime.datetime | None = Field(
        default=None, description="The date-time when processing of the job started."
    )
    finished_at: datetime.datetime | None = Field(
        default=None, description="The date-time when processing of the job finished."
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
    result: ResultT | None = Field(
        default=None, description="The upload result, when the job SUCCEEDED."
    )

    @classmethod
    def from_job(
        cls, job: model.UploadJob, result_class: type[ResultT] | None = None
    ) -> "UploadJobResponse[ResultT]":
        """Create the response for a job, parsing its result if it has one.

        Args:
            job: The upload job.
            result_class: Model class of the result; required to include it.

        Returns:
            The response.
        """
        assert job.id is not None
        result = None
        if result_class is not None and job.result_json is not None:
            result = result_class.model_validate_json(job.result_json)
        return cls(
            id=job.id,
            status=job.status,
            submitted_at=job.submitted_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
            error_status_code=job.error_status_code,
            error_detail=job.error_detail,
            result=result,
        )
