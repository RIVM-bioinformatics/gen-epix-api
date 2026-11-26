"""Define the shared commondb system service contract.

`BaseSystemService` extends the application service lifecycle with handlers for
data resets, outages, package licenses, feature flags, and upload jobs. Concrete services
implement these operations; command dispatch and persistence remain with the
application and repository layers.
"""

import abc
from enum import Enum

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseService


class BaseSystemService(BaseService[BaseSystemRepository]):
    """Encapsulates system-level command registration and service contracts.

    Concrete services implement outage, package-license, feature-flag, and data
    reset operations while this base registers their command handlers and defines
    the service type.
    """

    SERVICE_TYPE = ServiceType.SYSTEM

    def register_handlers(self) -> None:
        """Register CRUD, outage, package-license, and feature-flag handlers."""
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.DeleteAllOperationalDataCommand, self.delete_all_operational_data)
        f(command.DeleteAllRefDataCommand, self.delete_all_ref_data)
        f(command.RetrieveOutagesCommand, self.retrieve_outages)
        f(command.RetrieveLicensesCommand, self.retrieve_licenses)
        f(command.RetrieveFeatureFlagsCommand, self.retrieve_feature_flags)
        f(command.SubmitUploadJobCommand, self.submit_upload_job)
        f(command.RetrieveUploadJobCommand, self.retrieve_upload_job)

    @abc.abstractmethod
    def register_policies(self) -> None:
        """Register policies that enforce current system outage constraints.

        Raises:
            NotImplementedError: Always; concrete services register their policies.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        """Retrieve active and scheduled system outages.

        Args:
            cmd: Command requesting system outages.

        Returns:
            Active and scheduled outages.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        """Retrieve license metadata for installed packages.

        Args:
            cmd: Command requesting package license metadata.

        Returns:
            Installed package license metadata.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[Enum, bool]:
        """Retrieve the application's feature-flag configuration.

        Args:
            cmd: Command requesting feature flags.

        Returns:
            Feature flags keyed by their names.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def submit_upload_job(self, cmd: command.SubmitUploadJobCommand) -> model.UploadJob:
        """Accept an upload command for processing in the background.

        Args:
            cmd: Command wrapping the upload command.

        Returns:
            The accepted job, with status QUEUED.

        Raises:
            NotImplementedError: Always; concrete services implement submission.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_upload_job(
        self, cmd: command.RetrieveUploadJobCommand
    ) -> model.UploadJob:
        """Retrieve an upload job submitted by the requesting user.

        Args:
            cmd: Command identifying the job.

        Returns:
            The job, including its result once it has finished.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_all_operational_data(
        self, cmd: command.DeleteAllOperationalDataCommand
    ) -> model.DeleteAllOperationalDataResult:
        """Delete all operational data from the system.

        Args:
            cmd: Command requesting deletion of all operational data.

        Raises:
            NotImplementedError: Always; concrete services implement deletion.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_all_ref_data(
        self, cmd: command.DeleteAllRefDataCommand
    ) -> model.DeleteAllRefDataResult:
        """Delete application reference data after operational data is reset.

        Args:
            cmd: Command requesting deletion of application reference data.

        Raises:
            NotImplementedError: Always; concrete services implement deletion.
        """
        raise NotImplementedError()
