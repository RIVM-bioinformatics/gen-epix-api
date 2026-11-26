"""Implement commondb outage, feature-flag, and package-license services."""

import importlib
import importlib.metadata
import json
import logging
import re
import string
import threading
import tomllib
from enum import Enum
from typing import Any, ClassVar, cast

from cachetools import TTLCache, cached

from gen_epix.commondb import policies
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.policy import BaseHasSystemOutagePolicy
from gen_epix.commondb.domain.service import BaseSystemService
from gen_epix.commondb.policies.model_metadata_policy import ModelMetadataPolicy
from gen_epix.commondb.services.upload_job import UploadJobRunner
from gen_epix.fastapp import CrudOperation, EventTiming, exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain import Domain, Link
from gen_epix.util import get_package_root


class SystemService(BaseSystemService):
    """Encapsulates system configuration data and register global commondb policies."""

    REQUIREMENTS_FILE_NAME = "pyproject.toml"
    _PARSE_AND_GET_PACKAGE_METADATA_CACHE: ClassVar[TTLCache] = TTLCache(
        maxsize=1000, ttl=60
    )
    _UPLOAD_JOB_RUNNER_LOCK: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, app: App, **kwargs: Any) -> None:
        """Initialize configured concrete policy classes.

        Args:
            app: Application that owns this service.
            **kwargs: Additional base-service configuration.
        """
        super().__init__(app, **kwargs)
        app_impl: AppImplDetails = app.impl
        self.has_system_outage_policy_class: type[BaseHasSystemOutagePolicy] = (
            app_impl.get_mapped_class(policies.HasSystemOutagePolicy)
        )
        self.model_metadata_policy_class: type[ModelMetadataPolicy] = (
            app_impl.get_mapped_class(policies.ModelMetadataPolicy)
        )
        self._upload_job_runner: UploadJobRunner | None = None

    @property
    def upload_job_runner(self) -> UploadJobRunner:
        """Return the background runner for upload jobs, creating it on first use.

        Created lazily since the repository is not necessarily set when the
        service is initialized.
        """
        with SystemService._UPLOAD_JOB_RUNNER_LOCK:
            runner: UploadJobRunner | None = getattr(self, "_upload_job_runner", None)
            if runner is None:
                runner = UploadJobRunner(
                    app=self.app,
                    repository=self.repository,
                    generate_id=self.generate_id,
                    generate_timestamp=self.generate_timestamp,
                    logger=self.app.logger,
                )
                self._upload_job_runner = runner
            return runner

    @upload_job_runner.setter
    def upload_job_runner(self, runner: UploadJobRunner) -> None:
        """Replace the background runner for upload jobs."""
        self._upload_job_runner = runner

    def register_policies(self) -> None:
        """Register global outage and audit-metadata policies.

        The outage policy runs BEFORE other policies to short-circuit unavailable
        commands. Metadata masking runs AFTER all other policies.
        """
        # System outage policy should be BEFORE all other policies to short-circuit if there is an outage
        system_outage_policy = self.has_system_outage_policy_class(system_service=self)
        for command_class in self.app.domain.commands:
            self.app.register_policy(
                command_class, system_outage_policy, EventTiming.BEFORE
            )
        # Model metadata policy should be AFTER all other policies to ensure metadata is masked for unauthorized users even if they have access to the object itself based on other policies or
        model_metadata_policy = self.model_metadata_policy_class(
            role_set_map=self.app.impl.role_set_map
        )
        for cmd_class in self.app.domain.commands:
            self.app.register_policy(
                cmd_class, model_metadata_policy, EventTiming.AFTER
            )

    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        """Retrieve all configured system outages.

        Args:
            cmd: Command requesting outage records.

        Returns:
            Stored outage records.
        """
        with self.repository.uow() as uow:
            outages: list[model.Outage] = self.repository.crud(
                uow,
                None,
                model.Outage,
                CrudOperation.READ_ALL,
            )
        return outages

    def submit_upload_job(self, cmd: command.SubmitUploadJobCommand) -> model.UploadJob:
        """Authorize an upload command and queue it for background processing.

        The upload command's BEFORE policies are applied now, so that an upload
        the user is not allowed to execute is rejected immediately. The worker
        dispatches the upload command again as an initial command, applying all
        its policies.

        Args:
            cmd: Command wrapping the upload command.

        Returns:
            The accepted job, with status QUEUED.

        Raises:
            UnauthorizedAuthError: If there is no user, the upload command is
                issued by another user, or its BEFORE policies deny it.
            InitializationServiceError: If no handler is registered for the upload
                command.
            ServiceUnavailableError: If too many jobs are active in this process.
        """
        user = cmd.user
        if user is None or user.id is None:
            raise exc.UnauthorizedAuthError("d2a6f4c8", "Upload jobs require a user")
        upload_command = cmd.upload_command
        if upload_command.user is None:
            upload_command.user = user
        elif upload_command.user.id != user.id:
            raise exc.UnauthorizedAuthError(
                "e5c9b3a7", "The upload command must be issued by the submitting user"
            )
        self.app.get_handler(type(upload_command))
        self.app.pdp.apply(upload_command, EventTiming.BEFORE)
        return self.upload_job_runner.submit(user.id, upload_command)

    def retrieve_upload_job(
        self, cmd: command.RetrieveUploadJobCommand
    ) -> model.UploadJob:
        """Retrieve an upload job submitted by the requesting user.

        A job of another user, or of another job type than requested, is reported
        as non-existent so that its existence is not disclosed.

        Args:
            cmd: Command identifying the job.

        Returns:
            The job, reported as FAILED if its worker has stopped.

        Raises:
            UnauthorizedAuthError: If there is no user.
            InvalidIdsError: If the job does not exist, belongs to another user or
                is of another job type.
        """
        user = cmd.user
        if user is None or user.id is None:
            raise exc.UnauthorizedAuthError("b7f1d5e9", "Upload jobs require a user")
        try:
            job = self.upload_job_runner.read(cmd.job_id)
        except exc.InvalidIdsError as exception:
            raise exc.InvalidIdsError(
                "c3e8a6d4", "Upload job not found", ids=[cmd.job_id]
            ) from exception
        if job.user_id != user.id or (
            cmd.job_type is not None and job.job_type != cmd.job_type
        ):
            raise exc.InvalidIdsError(
                "f9b4c2e7", "Upload job not found", ids=[cmd.job_id]
            )
        return job

    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[Enum, bool]:
        """Retrieve feature flags currently configured on the application.

        Args:
            cmd: Command requesting feature-flag configuration.

        Returns:
            Mapping of feature-flag names to enabled states.
        """
        return self.app.feature_flags

    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        """Retrieve metadata for the application and installed dependencies.

        Args:
            cmd: Command requesting package license metadata.

        Returns:
            Package names, versions, licenses, and homepages when available.
        """
        packages = SystemService._parse_and_get_package_metadata()
        return packages

    def delete_all_operational_data(
        self, cmd: command.DeleteAllOperationalDataCommand
    ) -> model.DeleteAllOperationalDataResult:
        """Delete all operational data from the system.

        Each model is deleted in batches of the size the command prescribes, one
        commit per batch, so that memory use, transaction size and lock footprint stay
        bounded and an interrupted reset can be resumed by running it again.

        Args:
            cmd: Command requesting deletion of all operational data.

        Returns:
            DeleteAllOperationalDataResult. The `success` attribute indicates overall
            success, and `details` provides the number of deleted records per model
            class as a string. If an error occurred during deletion, the `details`
            entry for the model class contains the error message instead.
        """
        retval = model.DeleteAllOperationalDataResult(success=True)
        for model_class in cmd.SORTED_OPERATIONAL_DATA_MODEL_CLASSES:
            crud_command_class = self.app.domain.get_crud_command_for_model(model_class)
            batch_size = cmd.get_batch_size(model_class)
            model_name = model_class.ENTITY.name
            n_deleted = 0
            n_batches = 0
            try:
                while True:
                    n_batch = self.app.handle(
                        crud_command_class(
                            operation=CrudOperation.DELETE_ALL,
                            return_count=True,
                            limit=batch_size,
                        )
                    )
                    n_batches += 1
                    n_deleted += n_batch
                    self._log_delete_all_progress(
                        "d898a64f",
                        f"Deleted batch {n_batches} of {model_name}: "
                        f"{n_batch} records, {n_deleted} in total",
                        model_name,
                        batch_size,
                        n_batches,
                        n_batch,
                        n_deleted,
                    )
                    if n_batch < batch_size:
                        break
                retval.details[model_name] = str(n_deleted)
                self._log_delete_all_progress(
                    "b7e26ffc",
                    f"Deleted all {n_deleted} records of {model_name} "
                    f"in {n_batches} batches",
                    model_name,
                    batch_size,
                    n_batches,
                    0,
                    n_deleted,
                )
            except Exception as e:
                retval.success = False
                retval.details[model_name] = f"{type(e).__name__}: {e}"
                self._log_delete_all_progress(
                    "bfe88bc3",
                    f"Deleting {model_name} failed after {n_deleted} records "
                    f"in {n_batches} batches: {type(e).__name__}: {e}",
                    model_name,
                    batch_size,
                    n_batches,
                    0,
                    n_deleted,
                    level=logging.ERROR,
                )
        return retval

    def _log_delete_all_progress(
        self,
        code: str,
        msg: str,
        model_name: str,
        batch_size: int,
        n_batches: int,
        n_batch: int,
        n_deleted: int,
        level: int = logging.INFO,
    ) -> None:
        """Log the progress of deleting all records of a model, if logging is set up.

        Args:
            code: Log message code.
            msg: Human-readable message.
            model_name: Name of the model being deleted.
            batch_size: Number of records per batch for the model.
            n_batches: Number of batches executed so far.
            n_batch: Number of records deleted by the last batch.
            n_deleted: Number of records deleted so far for the model.
            level: Logging level.
        """
        if not self._logger:
            return
        self._logger.log(
            level,
            self.create_log_message(
                code,
                msg,
                add_debug_info=False,
                props={
                    "model": model_name,
                    "batch_size": batch_size,
                    "n_batches": n_batches,
                    "n_batch": n_batch,
                    "n_deleted": n_deleted,
                },
            ),
        )

    def delete_all_ref_data(
        self, cmd: command.DeleteAllRefDataCommand
    ) -> model.DeleteAllRefDataResult:
        """Delete application reference data after operational data is reset.

        The operation first asks the composed domain for every persistable model that
        links to a model in the application's reference-data list. Any remaining
        records prevent the reset. This derives the precondition from domain links
        rather than duplicating the operational command's model list.

        Args:
            cmd: Command requesting deletion of reference data.

        Returns:
            DeleteAllRefDataResult. The ``success`` attribute is false when
            operational records remain or a deletion fails. ``details`` contains
            deleted IDs per reference model or the relevant error message.
        """
        domain = self.app.domain
        retval = model.DeleteAllRefDataResult(success=True)

        ref_model_classes = set(cmd.SORTED_REF_DATA_MODEL_CLASSES)
        operational_model_classes = self._get_models_linked_to_ref_data(
            domain, ref_model_classes
        )

        # Do not remove reference data while operational records still reference it.
        for model_class in operational_model_classes:
            try:
                crud_command_class = domain.get_crud_command_for_model(model_class)
                records = self.app.handle(
                    crud_command_class(
                        user=None,
                        operation=CrudOperation.READ_ALL,
                        limit=1,
                        return_id=True,
                    )
                )
            except Exception as e:
                retval.success = False
                retval.details[model_class.ENTITY.name] = f"{type(e).__name__}: {e}"
                continue
            if records:
                retval.success = False
                retval.details[model_class.ENTITY.name] = (
                    "Operational data remains (at least one record); "
                    "delete all operational data before deleting reference data."
                )

        if not retval.success:
            return retval

        # Children before parents so foreign-key constraints are not violated.
        for model_class in cmd.SORTED_REF_DATA_MODEL_CLASSES:
            try:
                crud_command_class = domain.get_crud_command_for_model(model_class)
            except Exception as e:
                retval.success = False
                retval.details[model_class.ENTITY.name] = f"{type(e).__name__}: {e}"
                continue
            try:
                deleted_ids = self.app.handle(
                    crud_command_class(
                        user=cmd.user,
                        operation=CrudOperation.DELETE_ALL,
                        return_id=True,
                    )
                )
                retval.details[model_class.ENTITY.name] = json.dumps(
                    [str(x) for x in deleted_ids]
                )
            except Exception as e:
                retval.success = False
                retval.details[model_class.ENTITY.name] = f"{type(e).__name__}: {e}"
        return retval

    @staticmethod
    def _get_models_linked_to_ref_data(
        domain: Domain, ref_model_classes: set[type[Any]]
    ) -> list[type[Any]]:
        """Return persisted models that link to the reference-data model set.

        The domain stores links on the model that owns a foreign-key field. Walking
        the reverse link graph identifies operational rows that would prevent the
        reference rows from being deleted, including models in another service type.
        The walk continues transitively so a dependent model is checked even when it
        links through another operational model.
        """
        persistable_models = domain.get_dag_sorted_models(persistable=True)
        linked_models = set(ref_model_classes)
        while True:
            newly_linked_models = {
                model_class
                for model_class in persistable_models
                if model_class not in linked_models
                and any(
                    link.link_model_class in linked_models
                    for link in cast(
                        dict[int, Link], domain.get_model_links(model_class)
                    ).values()
                )
            }
            if not newly_linked_models:
                break
            linked_models.update(newly_linked_models)

        return [
            model_class
            for model_class in domain.get_dag_sorted_models(
                persistable=True, reverse=True
            )
            if model_class in linked_models and model_class not in ref_model_classes
        ]

    @staticmethod
    @cached(cache=_PARSE_AND_GET_PACKAGE_METADATA_CACHE)
    def _parse_and_get_package_metadata() -> list[model.PackageMetadata]:
        """Parse package metadata from pyproject.toml and installed dependencies."""
        pyproject_path = get_package_root() / SystemService.REQUIREMENTS_FILE_NAME
        packages: list[model.PackageMetadata] = []

        if not pyproject_path.exists():
            return packages

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        packages.append(
            model.PackageMetadata(
                name="gen-epix-api",
                version=pyproject_data["project"].get("version", None),
                license=pyproject_data["project"].get("license", None),
                homepage=pyproject_data["project"].get("urls", {}).get("Homepage"),
            )
        )

        # Extract dependencies from project.dependencies
        dependencies = pyproject_data.get("project", {}).get("dependencies", [])

        for dependency in dependencies:
            # Extract package name (everything before version specifiers)
            match = re.match(r"^([a-zA-Z0-9_-]+)", dependency)
            if match:
                package_name = match.group(1)
                # Get metadata for this package
                try:
                    metadata = importlib.metadata.metadata(package_name)

                    # Try to get homepage from Home-page field first
                    homepage = metadata.get("Home-page", "")

                    # If no Home-page, extract from Project-URL using well-known labels
                    if not homepage:
                        project_urls = metadata.get("Project-URL", "")
                        homepage = SystemService._extract_homepage_from_project_urls(
                            project_urls
                        )

                    package_metadata = model.PackageMetadata(
                        name=metadata.get("Name", package_name),
                        version=metadata.get("Version", ""),
                        license=metadata.get("License"),
                        homepage=homepage or None,  # Convert empty string to None
                    )
                    packages.append(package_metadata)
                except importlib.metadata.PackageNotFoundError:
                    # Package not installed or name doesn't match, skip it
                    continue

        return packages

    @staticmethod
    def _normalize_project_url_label(label: str) -> str:
        """Normalize project URL label according to PEP 753."""
        chars_to_remove = string.punctuation + string.whitespace
        removal_map = str.maketrans("", "", chars_to_remove)
        return label.translate(removal_map).lower()

    @staticmethod
    def _extract_homepage_from_project_urls(project_urls_str: str) -> str:
        """Extract a homepage URL using well-known Project-URL labels.

        Labels follow the Python packaging specification for well-known project URLs.
        """
        if not project_urls_str:
            return ""

        # Parse Project-URL entries (format: "label, url")
        urls = {}
        for entry in project_urls_str.split("\n"):
            entry = entry.strip()
            if ", " in entry:
                label, url = entry.split(", ", 1)
                normalized_label = SystemService._normalize_project_url_label(label)
                urls[normalized_label] = url.strip()

        # Priority order based on well-known labels for homepage
        priority_labels = [
            "homepage",
            "documentation",
            "docs",
            "repository",
            "sourcecode",
            "github",
            "source",
        ]

        for label in priority_labels:
            if label in urls:
                return urls[label]

        # If no well-known labels found, return first URL available
        return next(iter(urls.values())) if urls else ""
