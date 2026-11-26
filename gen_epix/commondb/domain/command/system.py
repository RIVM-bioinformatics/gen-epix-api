"""Define shared commondb commands for system-level operations.

The public types cover operational and reference-data resets, outage CRUD, and
retrieval of outage, license, and feature-flag metadata. They are dispatched
through the application layer; transport and persistence remain outside this
module.
"""

from typing import ClassVar
from uuid import UUID

from pydantic import Field, SerializeAsAny

from gen_epix.commondb.domain import model
from gen_epix.commondb.domain.command.base import Command, CrudCommand

# Non-CRUD commands


class DeleteAllOperationalDataCommand(Command):
    """Represents a request to execute deletion of one application's operational data.

    This is intended as a maintenance operation or for use during development, and
    should only be executable under specific conditions. Non-operational data are
    not affected.
    """

    SORTED_OPERATIONAL_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = (
        []
    )  # Persistable domain models for operational data, in deletion order so that foreign-key constraints do not fail (i.e. reverse DAG order on links)
    BATCH_SIZE: ClassVar[int] = 1000  # Rows deleted per batch, one commit per batch
    BATCH_SIZE_BY_MODEL: ClassVar[dict[type[model.ModelNoId], int]] = (
        {}
    )  # Per-model override of BATCH_SIZE, e.g. for large or heavily indexed tables

    @classmethod
    def get_batch_size(cls, model_class: type[model.ModelNoId]) -> int:
        """Return the number of rows to delete per batch for a model.

        Args:
            model_class: Operational model to delete.

        Returns:
            The per-model override when configured, otherwise BATCH_SIZE.
        """
        return cls.BATCH_SIZE_BY_MODEL.get(model_class, cls.BATCH_SIZE)


class DeleteAllRefDataCommand(Command):
    """Represents a request to execute deletion of application reference data.

    Application domains subclass this command and provide their reference-data
    models in deletion order after the operational-data reset. The shared command
    deliberately has no model list; application composition determines the
    concrete command and model set.
    """

    SORTED_REF_DATA_MODEL_CLASSES: ClassVar[list[type[model.ModelNoId]]] = []


class RetrieveOutagesCommand(Command):
    """Represents a request to execute retrieval of system outage information."""

    pass


class RetrieveLicensesCommand(Command):
    """Represents a request to execute retrieval of installed-package licenses."""

    pass


class RetrieveFeatureFlagsCommand(Command):
    """Represents a request to execute retrieval of composed-application flags."""

    pass


class SubmitUploadJobCommand(Command):
    """Represents a request to process an upload command in the background.

    The upload command is authorized for the submitting user before the job is
    accepted, and is dispatched again as an initial command, with all its policies,
    when a background worker processes it. A job can therefore do nothing that the
    user could not do by executing the upload command directly. The upload command
    must be issued by the same user as this command.
    """

    upload_command: SerializeAsAny[Command] = Field(
        description="The upload command to process in the background."
    )


class RetrieveUploadJobCommand(Command):
    """Represents a request to retrieve the status and result of an upload job.

    Only the user that submitted the job can retrieve it.
    """

    job_id: UUID = Field(description="The ID of the upload job.")
    job_type: str | None = Field(
        default=None,
        description="If given, the job is only returned if it processes this upload command.",
        max_length=100,
    )


# CRUD commands


class OutageCrudCommand(CrudCommand):
    """Represents a request to execute CRUD operations on system outage windows."""

    MODEL_CLASS: ClassVar = model.Outage


class UploadJobCrudCommand(CrudCommand):
    """Represents a request to execute CRUD operations on upload jobs.

    Jobs are created and updated by the system service; this command gives
    administrators read access for monitoring.
    """

    MODEL_CLASS: ClassVar = model.UploadJob
