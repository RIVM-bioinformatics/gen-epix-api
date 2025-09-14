import importlib
import importlib.metadata
import re
import string
import tomllib

from cachetools import TTLCache, cached

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.service import BaseSystemService
from gen_epix.commondb.policies.has_system_outage_policy import HasSystemOutagePolicy
from gen_epix.commondb.util import get_project_root
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
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        with self.repository.uow() as uow:
            outages: list[model.Outage] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    None,
                    model.Outage,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                )
            )
        return outages

    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        packages = SystemService._parse_and_get_package_metadata()
        return packages

    @staticmethod
    @cached(cache=TTLCache(maxsize=1000, ttl=60))
    def _parse_and_get_package_metadata() -> list[model.PackageMetadata]:
        """
        Parse pyproject.toml, extract package names, and get their metadata.
        """
        pyproject_path = get_project_root() / SystemService.REQUIREMENTS_FILE_NAME
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
        """
        Extract homepage URL from Project-URL metadata using well-known labels:
        (https://packaging.python.org/en/latest/specifications/well-known-project-urls/#well-known-labels)
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
