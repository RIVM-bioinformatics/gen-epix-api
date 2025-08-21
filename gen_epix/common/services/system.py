import importlib
import re
import tomllib

from gen_epix.common.domain import command, model
from gen_epix.common.domain.service import BaseSystemService
from gen_epix.common.policies.has_system_outage_policy import HasSystemOutagePolicy
from gen_epix.common.util import get_project_root
from gen_epix.fastapp import CrudOperation, EventTiming


class SystemService(BaseSystemService):
    REQUIREMENTS_FILE_NAME = "pyproject.toml"

    def register_policies(self) -> None:
        """
        Registers policies that checks if the system has a current outage

        """
        policy = HasSystemOutagePolicy(system_service=self)
        for command_class in self.app.domain.commands:
            self.app.register_policy(command_class, policy, EventTiming.BEFORE)

    def retrieve_outages(
        self, _cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        with self.repository.uow() as uow:
            outages = self.repository.crud(
                uow,
                None,
                model.Outage,
                None,
                None,
                CrudOperation.READ_ALL,
            )
        return outages

    def retrieve_licenses(
        self, _cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        packages = SystemService._parse_and_get_package_metadata()
        return packages

    @staticmethod
    def _parse_and_get_package_metadata() -> list[model.PackageMetadata]:
        """Parse pyproject.toml, extract package names, and get their metadata."""
        pyproject_path = get_project_root() / SystemService.REQUIREMENTS_FILE_NAME
        packages = []

        if not pyproject_path.exists():
            return packages

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        packages.append(
            model.PackageMetadata(
                name="gen-epix-api",
                version=pyproject_data["project"].get("version", None),
                license=pyproject_data["project"].get("license", None),
                homepage=pyproject_data["project"]["urls"].get("Homepage", None),
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
                    package_metadata = model.PackageMetadata(
                        name=metadata.get("Name", package_name),
                        version=metadata.get("Version"),
                        license=metadata.get("License"),
                        homepage=metadata.get("Home-page"),
                    )
                    packages.append(package_metadata)
                except importlib.metadata.PackageNotFoundError:
                    # Package not installed or name doesn't match, skip it
                    continue

        return packages
