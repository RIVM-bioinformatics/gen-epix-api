import datetime
import importlib
import importlib.metadata
import re
import string
import tomllib
import uuid
from collections.abc import Hashable
from typing import Any

from cachetools import TTLCache, cached
from sqlalchemy import Engine
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from gen_epix.commondb import policies
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.policy import BaseHasSystemOutagePolicy
from gen_epix.commondb.domain.service import BaseSystemService
from gen_epix.commondb.policies.model_metadata_policy import ModelMetadataPolicy
from gen_epix.fastapp import CrudOperation, EventTiming
from gen_epix.fastapp.app import App
from gen_epix.fastapp.repositories.dict import DictRepository
from gen_epix.fastapp.repositories.sa.mapper import BaseSAMapper
from gen_epix.fastapp.repositories.sa.repository import SARepository
from gen_epix.util import get_package_root


class SystemService(BaseSystemService):
    REQUIREMENTS_FILE_NAME = "pyproject.toml"

    def __init__(self, app: App, **kwargs: Any) -> None:
        super().__init__(app, **kwargs)
        app_impl: AppImplDetails = app.impl
        self.has_system_outage_policy_class: type[BaseHasSystemOutagePolicy] = (
            app_impl.get_mapped_class(policies.HasSystemOutagePolicy)
        )
        self.model_metadata_policy_class: type[ModelMetadataPolicy] = (
            app_impl.get_mapped_class(policies.ModelMetadataPolicy)
        )

    def register_policies(self) -> None:
        """
        Registers policies that checks if the system has a current outage

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
        with self.repository.uow() as uow:
            outages: list[model.Outage] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    None,
                    model.Outage,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                )
            )
        return outages

    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[Hashable, bool]:
        return self.app.feature_flags

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

    def export_database(self, cmd: command.ExportDatabaseCommand) -> bytes:
        """
        Export all application data as a SQL script usable in Azure Data Studio
        to re-create the database locally. Generates INSERT statements for all
        tables registered across the app's repositories (SA or Dict).
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        lines: list[str] = [
            "-- Database export generated by Gen-EpiX\n",
            f"-- Generated at: {now}\n",
            "-- For use with Azure Data Studio / SQL Server\n",
            "-- Run the full script in a single transaction to maintain integrity.\n\n",
            "BEGIN TRANSACTION;\n\n",
        ]

        # --- SA repositories ---
        # Group mappers by engine so each physical DB is exported once, even
        # when multiple service-type repositories share the same database.
        engine_to_mappers: dict[Engine, list[BaseSAMapper]] = {}
        for repository in self.app.impl.repositories.values():
            if not isinstance(repository, SARepository):
                continue
            engine = repository.engine
            engine_to_mappers.setdefault(engine, [])
            engine_to_mappers[engine].extend(repository.mappers)

        for engine, mappers in engine_to_mappers.items():
            dialect = engine.dialect.name

            def q(name: str, _dialect: str = dialect) -> str:  # noqa: E731
                return f"[{name}]" if _dialect == "mssql" else f'"{name}"'

            inspector = sa_inspect(engine)

            for mapper in mappers:
                schema_name = mapper.schema_name
                table_name = mapper.table_name
                columns = inspector.get_columns(table_name, schema=schema_name)
                col_names = [col["name"] for col in columns]

                qualified = (
                    f"{q(schema_name)}.{q(table_name)}"
                    if schema_name
                    else q(table_name)
                )
                cols_str = ", ".join(q(c) for c in col_names)

                # Detect identity/autoincrement columns for SQL Server
                has_identity = dialect == "mssql" and any(
                    col.get("identity") or col.get("autoincrement") is True
                    for col in columns
                )

                with engine.connect() as conn:
                    rows = conn.execute(
                        text(f"SELECT * FROM {qualified}")
                    ).fetchall()

                if not rows:
                    continue

                lines.append(f"-- {qualified}\n")
                if has_identity:
                    lines.append(f"SET IDENTITY_INSERT {qualified} ON;\n")

                for row in rows:
                    values_str = ", ".join(
                        SystemService._format_sql_value(v) for v in row
                    )
                    lines.append(
                        f"INSERT INTO {qualified} ({cols_str})"
                        f" VALUES ({values_str});\n"
                    )

                if has_identity:
                    lines.append(f"SET IDENTITY_INSERT {qualified} OFF;\n")
                lines.append("\n")

        # --- Dict repositories ---
        # Use model_dump() for column names/values; schema/table from ENTITY.
        seen_model_classes: set[type] = set()
        for repository in self.app.impl.repositories.values():
            if not isinstance(repository, DictRepository):
                continue
            for model_class, objs_by_id in repository.db.items():
                if model_class in seen_model_classes or not objs_by_id:
                    continue
                seen_model_classes.add(model_class)
                entity = model_class.ENTITY
                if entity is None:
                    continue
                schema_name: str | None = entity.schema_name
                table_name: str | None = entity.table_name
                if not table_name:
                    continue

                # Use mssql quoting to match target Azure Data Studio / SQL Server
                qualified = (
                    f"[{schema_name}].[{table_name}]"
                    if schema_name
                    else f"[{table_name}]"
                )

                objs = list(objs_by_id.values())
                col_names = list(objs[0].model_dump().keys())
                cols_str = ", ".join(f"[{c}]" for c in col_names)

                lines.append(f"-- {qualified}\n")
                for obj in objs:
                    row_dict = obj.model_dump()
                    values_str = ", ".join(
                        SystemService._format_sql_value(row_dict[c]) for c in col_names
                    )
                    lines.append(
                        f"INSERT INTO {qualified} ({cols_str})"
                        f" VALUES ({values_str});\n"
                    )
                lines.append("\n")

        lines.append("COMMIT;\n")
        return "".join(lines).encode("utf-8")

    @staticmethod
    def _format_sql_value(value: Any) -> str:
        """Format a Python value as a SQL literal."""
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, datetime.datetime):
            # SQL Server datetime only accepts 3-digit milliseconds (not
            # microseconds), use ISO 8601 format truncated to milliseconds.
            ms = value.microsecond // 1000
            return f"'{value.strftime('%Y-%m-%dT%H:%M:%S.')}{ms:03d}'"
        if isinstance(value, datetime.date):
            return f"'{value.strftime('%Y-%m-%d')}'"
        if isinstance(value, uuid.UUID):
            return f"'{value}'"
        if isinstance(value, bytes):
            return f"0x{value.hex()}"
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
